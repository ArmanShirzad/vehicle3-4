import pygame
import math

pygame.init()

# Setup Pygame window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 3 - Love and Exploration with Inhibitory Connections")

# Setup clock for controlling frame rate
clock = pygame.time.Clock()
fps = 60

# Setup font for labels
font = pygame.font.SysFont("consolas", 16)

# Vehicle 3 class with inhibitory connections (negative influence)
class VehicleThree:
    def __init__(self, x, y, radius=20, heading=0, config='a'):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.config = config  # 'a' (uncrossed inhibitory - LOVES), 'b' (crossed inhibitory - EXPLORER)
        self.sensor_dist = self.radius * 1.5
        self.sensor_angle_left = -0.5  # radians, ~28 degrees left
        self.sensor_angle_right = 0.5  # radians, ~28 degrees right
        self.scale = 0.01  # Scale factor for inhibitory influence
        self.base_speed = 2.0  # Base speed when stimulus is weak (inhibitory: strong stimulus slows down)

    def _sensor_position(self, angle):
        sensor_local_x = math.cos(angle) * self.sensor_dist
        sensor_local_y = math.sin(angle) * self.sensor_dist
        cos_heading = math.cos(self.heading)
        sin_heading = math.sin(self.heading)
        sensor_world_x = self.x + cos_heading * sensor_local_x - sin_heading * sensor_local_y
        sensor_world_y = self.y + sin_heading * sensor_local_x + cos_heading * sensor_local_y
        return (sensor_world_x, sensor_world_y)

    def _left_sensor_position(self):
        return self._sensor_position(self.sensor_angle_left)

    def _right_sensor_position(self):
        return self._sensor_position(self.sensor_angle_right)

    def _intensity_one(self, point_x, point_y, light_x, light_y):
        dx = light_x - point_x
        dy = light_y - point_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 0.1:
            return 1000.0
        base_intensity = 50.0
        intensity = base_intensity + (100.0 / (distance * 0.1))
        return intensity

    def _intensity_at(self, point_x, point_y, lights):
        return sum(self._intensity_one(point_x, point_y, light.x, light.y) for light in lights)

    def update(self, lights):
        left_pos = self._left_sensor_position()
        right_pos = self._right_sensor_position()
        left_intensity = self._intensity_at(left_pos[0], left_pos[1], lights)
        right_intensity = self._intensity_at(right_pos[0], right_pos[1], lights)

        # Inhibitory connections: strong stimulus slows down motor
        # Vehicle 3a: uncrossed (same-side) inhibitory - LOVES source, faces it
        # Vehicle 3b: crossed (opposite-side) inhibitory - EXPLORER, faces away
        if self.config == 'a':  # Uncrossed inhibitory: sensor affects same-side motor
            # Left sensor inhibits left motor, right sensor inhibits right motor
            left_motor = max(0.1, self.base_speed - left_intensity * self.scale)
            right_motor = max(0.1, self.base_speed - right_intensity * self.scale)
        elif self.config == 'b':  # Crossed inhibitory: sensor affects opposite-side motor
            # Left sensor inhibits right motor, right sensor inhibits left motor
            left_motor = max(0.1, self.base_speed - right_intensity * self.scale)
            right_motor = max(0.1, self.base_speed - left_intensity * self.scale)

        forward_speed = (left_motor + right_motor) / 2
        turning_rate = (right_motor - left_motor) / (self.radius * 2)

        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)

        # Wrap around screen edges
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        # Draw vehicle body as a green circle (different from Vehicle 2's blue)
        pygame.draw.circle(surface, (0, 200, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

        # Draw direction indicator (arrow showing heading)
        arrow_len = self.radius * 1.5
        arrow_end_x = self.x + math.cos(self.heading) * arrow_len
        arrow_end_y = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(surface, (0, 255, 0), (int(self.x), int(self.y)), (int(arrow_end_x), int(arrow_end_y)), 3)

        # Draw sensor positions as red circles
        left_pos = self._left_sensor_position()
        right_pos = self._right_sensor_position()
        pygame.draw.circle(surface, (255, 0, 0), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 0, 0), (int(right_pos[0]), int(right_pos[1])), 5)

        # Draw inhibitory connection indicators (dashed lines with minus signs)
        # Left sensor to motor connection
        if self.config == 'a':
            # Same-side: left sensor to left side of vehicle
            pygame.draw.line(surface, (200, 0, 0), (int(left_pos[0]), int(left_pos[1])), 
                           (int(self.x - self.radius * 0.7), int(self.y)), 1)
        else:  # config == 'b'
            # Crossed: left sensor to right side of vehicle
            pygame.draw.line(surface, (200, 0, 0), (int(left_pos[0]), int(left_pos[1])), 
                           (int(self.x + self.radius * 0.7), int(self.y)), 1)

        # Draw config label above vehicle
        if font:
            behavior_name = "LOVES" if self.config == 'a' else "EXPLORER"
            label_text = font.render(f"Vehicle 3{self.config} ({behavior_name})", True, (0, 0, 0))
            surface.blit(label_text, (int(self.x) - 40, int(self.y) - self.radius - 20))

# Light source class (represents attractive sources)
class Light:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, surface):
        # Draw as yellow circle (attractive source)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

# Create initial light sources
lights = []
lights.append(Light(WIDTH // 4, HEIGHT // 4))
lights.append(Light(3 * WIDTH // 4, 3 * HEIGHT // 4))

# Create vehicles with different configurations
vehicles = []
vehicles.append(VehicleThree(WIDTH // 2 - 200, HEIGHT // 2 - 100, heading=0, config='a'))  # 3a: LOVES (uncrossed)
vehicles.append(VehicleThree(WIDTH // 2 - 200, HEIGHT // 2 + 100, heading=math.pi / 2, config='b'))  # 3b: EXPLORER (crossed)

running = True
while running:
    screen.fill((255, 255, 255))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Add new light source on mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            lights.append(Light(event.pos[0], event.pos[1]))

    # Draw all light sources
    for light in lights:
        light.draw(screen)

    # Update and draw all vehicles
    for vehicle in vehicles:
        vehicle.update(lights)
        vehicle.draw(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()


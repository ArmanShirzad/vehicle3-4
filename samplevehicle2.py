import pygame
import math

pygame.init()

# Setup Pygame window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 2 - Fear and Aggression with Multiple Light Sources")

# Setup clock for controlling frame rate
clock = pygame.time.Clock()
fps = 60

# Setup font for labels (optional, but used for config labels)
font = pygame.font.SysFont("consolas", 16)

# Vehicle 2 class with two sensors and two motors, configurable connections (a, b, c)
class VehicleTwo:
    def __init__(self, x, y, radius=20, heading=0, config='a'):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.config = config  # 'a' (uncrossed/same-side), 'b' (crossed/opposite-side), 'c' (both to both)
        self.sensor_dist = self.radius * 1.5
        self.sensor_angle_left = -0.5  # radians, ~28 degrees left
        self.sensor_angle_right = 0.5  # radians, ~28 degrees right
        self.scale = 0.01  # Scale factor adjusted for multiple lights to prevent excessive speed

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
        base_temperature = 50.0
        intensity = base_temperature + (100.0 / (distance * 0.1))
        return intensity

    def _intensity_at(self, point_x, point_y, lights):
        return sum(self._intensity_one(point_x, point_y, light.x, light.y) for light in lights)

    def update(self, lights):
        left_pos = self._left_sensor_position()
        right_pos = self._right_sensor_position()
        left_intensity = self._intensity_at(left_pos[0], left_pos[1], lights)
        right_intensity = self._intensity_at(right_pos[0], right_pos[1], lights)

        if self.config == 'a':  # Uncovered (same-side): fear/coward - turns away
            left_motor = left_intensity * self.scale
            right_motor = right_intensity * self.scale
        elif self.config == 'b':  # Crossed (opposite-side): aggression - turns toward
            left_motor = right_intensity * self.scale
            right_motor = left_intensity * self.scale
        elif self.config == 'c':  # Both sensors to both motors: like Vehicle 1, minimal turning
            avg_intensity = (left_intensity + right_intensity) / 2
            left_motor = avg_intensity * self.scale
            right_motor = avg_intensity * self.scale

        forward_speed = (left_motor + right_motor) / 2
        turning_rate = (right_motor - left_motor) / (self.radius * 2)  # Approximate wheel base for turning

        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)

        # Wrap around screen edges
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        # Draw vehicle body as a blue circle
        pygame.draw.circle(surface, (0, 0, 255), (int(self.x), int(self.y)), self.radius)
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

        # Draw config label above vehicle
        if font:
            label_text = font.render(f"Vehicle 2{self.config}", True, (0, 0, 0))
            surface.blit(label_text, (int(self.x) - 20, int(self.y) - self.radius - 20))

# Light source class (represents heat/light sources)
class Light:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

# Create initial light sources (multiple)
lights = []
lights.append(Light(WIDTH // 4, HEIGHT // 4))
lights.append(Light(3 * WIDTH // 4, 3 * HEIGHT // 4))

# Create vehicles with different configurations and initial headings/positions
vehicles = []
vehicles.append(VehicleTwo(WIDTH // 2 - 200, HEIGHT // 2 - 100, heading=0, config='a'))  # Fear/coward
vehicles.append(VehicleTwo(WIDTH // 2 - 200, HEIGHT // 2, heading=math.pi / 2, config='b'))  # Aggression
vehicles.append(VehicleTwo(WIDTH // 2 - 200, HEIGHT // 2 + 100, heading=math.pi, config='c'))  # Luxurious Vehicle 1-like

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
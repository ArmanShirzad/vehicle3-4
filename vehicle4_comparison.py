"""
Vehicle 4 Comparison: Non-Linear (Gaussian) vs Linear (Monotonic) Response

This demonstrates the key difference between:
- Vehicle 4a: Non-monotonic/Gaussian response (has a PEAK - optimal intensity)
- Linear Vehicle: Monotonic response (the more intensity, the more motor speed)

According to Braitenberg:
- Monotonic: "the more the sensor was excited, the faster the corresponding motor ran"
- Non-monotonic: "motor reaches a maximum, beyond this point... the speed will decrease again"
"""

import pygame
import math
from typing import List, Literal, Union
from enum import Enum

pygame.init()

# Setup Pygame window
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 4 Comparison: Gaussian vs Linear Response")

clock = pygame.time.Clock()
fps = 60

# Fonts - using system fonts with character
font = pygame.font.SysFont("monaco", 12)
font_medium = pygame.font.SysFont("monaco", 14)
font_large = pygame.font.SysFont("monaco", 16, bold=True)
font_title = pygame.font.SysFont("monaco", 20, bold=True)

# Color Palette - Industrial/Technical
BG_COLOR = (28, 32, 38)           # Dark charcoal
GRID_COLOR = (45, 52, 62)         # Subtle grid
TEXT_PRIMARY = (220, 225, 230)    # Off-white
TEXT_DIM = (120, 130, 145)        # Muted text
ACCENT_TEAL = (0, 210, 190)       # Gaussian vehicle
ACCENT_ORANGE = (255, 140, 50)    # Linear vehicle
GRAPH_BG = (38, 44, 52)           # Graph background
DIVIDER_COLOR = (60, 70, 85)      # Section dividers


class SourceType(Enum):
    LIGHT = "Light"


class Source:
    def __init__(self, x: float, y: float, source_type: SourceType = SourceType.LIGHT, radius: int = 18):
        self.x = x
        self.y = y
        self.source_type = source_type
        self.radius = radius

    def draw(self, surface: pygame.Surface) -> None:
        # Glow effect
        for i in range(3, 0, -1):
            alpha_color = (255, 255, 100, 50)
            pygame.draw.circle(surface, (80 + i*20, 80 + i*15, 30), 
                             (int(self.x), int(self.y)), self.radius + i*4)
        # Core
        pygame.draw.circle(surface, (255, 230, 100), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (200, 180, 50), (int(self.x), int(self.y)), self.radius, 2)


class VehicleGaussian:
    """
    Vehicle 4a: NON-LINEAR (Gaussian Bell Curve) Response
    
    Response function: exp(-((intensity - optimal)^2) / (2 * width^2))
    
    - Has a PEAK at optimal intensity
    - Below optimal: approaching behavior (motor speeds up)
    - Above optimal: avoiding behavior (motor slows down)
    - Result: ORBITING around sources at optimal distance
    """
    def __init__(self, x: float, y: float, radius: int = 22, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius * 1.4
        self.sensor_angle = 0.6
        
        self.base_speed = 1.2
        self.max_motor_boost = 2.5
        
        # Gaussian curve parameters
        self.optimal_intensity = 120.0  # Peak response at this intensity
        self.curve_width = 80.0         # Width of bell curve (sigma)
        
        self.left_motor_speed = 0.0
        self.right_motor_speed = 0.0
        self.left_intensity = 0.0
        self.right_intensity = 0.0
        
        # Trail for visualization
        self.trail: List[tuple] = []
        self.max_trail_length = 200

    def _sensor_position(self, angle: float) -> tuple[float, float]:
        sensor_local_x = math.cos(angle) * self.sensor_dist
        sensor_local_y = math.sin(angle) * self.sensor_dist
        cos_h = math.cos(self.heading)
        sin_h = math.sin(self.heading)
        return (
            self.x + cos_h * sensor_local_x - sin_h * sensor_local_y,
            self.y + sin_h * sensor_local_x + cos_h * sensor_local_y
        )

    def _intensity_at(self, px: float, py: float, sources: List[Source]) -> float:
        total = 0.0
        for src in sources:
            dx, dy = src.x - px, src.y - py
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 1.0:
                dist = 1.0
            total += 40000.0 / (dist * dist)  # Inverse square law
        return total

    def _gaussian_response(self, intensity: float) -> float:
        """
        GAUSSIAN (Bell Curve) - The key non-linear function!
        
        Returns maximum (1.0) when intensity == optimal_intensity
        Falls off symmetrically on both sides
        """
        diff = intensity - self.optimal_intensity
        exponent = -(diff * diff) / (2 * self.curve_width * self.curve_width)
        return math.exp(exponent)

    def update(self, sources: List[Source]) -> None:
        left_motor = self.base_speed
        right_motor = self.base_speed

        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)

        self.left_intensity = self._intensity_at(left_pos[0], left_pos[1], sources)
        self.right_intensity = self._intensity_at(right_pos[0], right_pos[1], sources)
        
        # Apply GAUSSIAN response (non-linear!)
        left_response = self._gaussian_response(self.left_intensity) * self.max_motor_boost
        right_response = self._gaussian_response(self.right_intensity) * self.max_motor_boost
        
        # Crossed connections (like Vehicle 2b - approaches)
        left_motor += right_response
        right_motor += left_response

        self.left_motor_speed = max(0.0, left_motor)
        self.right_motor_speed = max(0.0, right_motor)

        forward_speed = (self.left_motor_speed + self.right_motor_speed) / 2
        turning_rate = (self.left_motor_speed - self.right_motor_speed) / (self.radius * 1.5)

        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)

        # Keep in bounds (left half of screen)
        self.x = max(20, min(WIDTH // 2 - 30, self.x))
        self.y = max(180, min(HEIGHT - 20, self.y))
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def draw(self, surface: pygame.Surface) -> None:
        # Draw trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = int(255 * (i / len(self.trail)))
                color = (0, alpha // 2, alpha // 2 + 50)
                pygame.draw.line(surface, color, 
                               (int(self.trail[i][0]), int(self.trail[i][1])),
                               (int(self.trail[i+1][0]), int(self.trail[i+1][1])), 2)
        
        # Vehicle body
        pygame.draw.circle(surface, ACCENT_TEAL, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 255, 230), (int(self.x), int(self.y)), self.radius, 2)

        # Direction arrow
        arrow_len = self.radius * 1.4
        ax = self.x + math.cos(self.heading) * arrow_len
        ay = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(surface, (255, 255, 255), 
                        (int(self.x), int(self.y)), (int(ax), int(ay)), 3)

        # Sensors
        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)
        pygame.draw.circle(surface, (255, 80, 80), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 80, 80), (int(right_pos[0]), int(right_pos[1])), 5)

        # Label
        label = font_large.render("GAUSSIAN", True, ACCENT_TEAL)
        surface.blit(label, (int(self.x) - 40, int(self.y) - self.radius - 22))


class VehicleLinear:
    """
    LINEAR (Monotonic) Response - Vehicle 3 style
    
    Response function: intensity * slope (capped)
    
    - "The more, the more" - motor speed increases linearly with intensity
    - NO peak, NO optimal intensity
    - Result: Approaches source directly, may crash into it or oscillate wildly
    """
    def __init__(self, x: float, y: float, radius: int = 22, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius * 1.4
        self.sensor_angle = 0.6
        
        self.base_speed = 1.2
        self.max_motor_boost = 2.5
        
        # Linear parameters
        self.linear_slope = 0.02       # How much motor speed increases per intensity unit
        self.intensity_scale = 1.0     # Scale factor for intensity
        
        self.left_motor_speed = 0.0
        self.right_motor_speed = 0.0
        self.left_intensity = 0.0
        self.right_intensity = 0.0
        
        # Trail
        self.trail: List[tuple] = []
        self.max_trail_length = 200

    def _sensor_position(self, angle: float) -> tuple[float, float]:
        sensor_local_x = math.cos(angle) * self.sensor_dist
        sensor_local_y = math.sin(angle) * self.sensor_dist
        cos_h = math.cos(self.heading)
        sin_h = math.sin(self.heading)
        return (
            self.x + cos_h * sensor_local_x - sin_h * sensor_local_y,
            self.y + sin_h * sensor_local_x + cos_h * sensor_local_y
        )

    def _intensity_at(self, px: float, py: float, sources: List[Source]) -> float:
        total = 0.0
        for src in sources:
            dx, dy = src.x - px, src.y - py
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 1.0:
                dist = 1.0
            total += 40000.0 / (dist * dist)
        return total

    def _linear_response(self, intensity: float) -> float:
        """
        LINEAR (Monotonic) - Simple proportional response!
        
        "The more the sensor was excited, the faster the motor ran"
        Just multiplies intensity by slope, capped at 1.0
        """
        response = intensity * self.linear_slope * self.intensity_scale
        return min(1.0, response)  # Cap at 1.0

    def update(self, sources: List[Source]) -> None:
        left_motor = self.base_speed
        right_motor = self.base_speed

        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)

        self.left_intensity = self._intensity_at(left_pos[0], left_pos[1], sources)
        self.right_intensity = self._intensity_at(right_pos[0], right_pos[1], sources)
        
        # Apply LINEAR response (monotonic!)
        left_response = self._linear_response(self.left_intensity) * self.max_motor_boost
        right_response = self._linear_response(self.right_intensity) * self.max_motor_boost
        
        # Crossed connections (like Vehicle 2b - approaches)
        left_motor += right_response
        right_motor += left_response

        self.left_motor_speed = max(0.0, left_motor)
        self.right_motor_speed = max(0.0, right_motor)

        forward_speed = (self.left_motor_speed + self.right_motor_speed) / 2
        turning_rate = (self.left_motor_speed - self.right_motor_speed) / (self.radius * 1.5)

        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)

        # Keep in bounds (right half of screen)
        self.x = max(WIDTH // 2 + 30, min(WIDTH - 20, self.x))
        self.y = max(180, min(HEIGHT - 20, self.y))
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def draw(self, surface: pygame.Surface) -> None:
        # Draw trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                alpha = int(255 * (i / len(self.trail)))
                color = (alpha // 2 + 50, alpha // 3, 0)
                pygame.draw.line(surface, color, 
                               (int(self.trail[i][0]), int(self.trail[i][1])),
                               (int(self.trail[i+1][0]), int(self.trail[i+1][1])), 2)
        
        # Vehicle body
        pygame.draw.circle(surface, ACCENT_ORANGE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 180, 100), (int(self.x), int(self.y)), self.radius, 2)

        # Direction arrow
        arrow_len = self.radius * 1.4
        ax = self.x + math.cos(self.heading) * arrow_len
        ay = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(surface, (255, 255, 255), 
                        (int(self.x), int(self.y)), (int(ax), int(ay)), 3)

        # Sensors
        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)
        pygame.draw.circle(surface, (255, 80, 80), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 80, 80), (int(right_pos[0]), int(right_pos[1])), 5)

        # Label
        label = font_large.render("LINEAR", True, ACCENT_ORANGE)
        surface.blit(label, (int(self.x) - 28, int(self.y) - self.radius - 22))


def draw_response_graph(surface: pygame.Surface, x: int, y: int, width: int, height: int,
                        vehicle_gaussian: VehicleGaussian, vehicle_linear: VehicleLinear) -> None:
    """Draw the response function comparison graph."""
    # Background
    pygame.draw.rect(surface, GRAPH_BG, (x, y, width, height))
    pygame.draw.rect(surface, DIVIDER_COLOR, (x, y, width, height), 2)
    
    # Title
    title = font_large.render("Response Functions: Motor Speed vs Intensity", True, TEXT_PRIMARY)
    surface.blit(title, (x + 10, y + 8))
    
    # Graph area
    graph_x = x + 60
    graph_y = y + 40
    graph_w = width - 80
    graph_h = height - 70
    
    # Axes
    pygame.draw.line(surface, TEXT_DIM, (graph_x, graph_y + graph_h), 
                    (graph_x + graph_w, graph_y + graph_h), 2)  # X axis
    pygame.draw.line(surface, TEXT_DIM, (graph_x, graph_y), 
                    (graph_x, graph_y + graph_h), 2)  # Y axis
    
    # Axis labels
    x_label = font.render("Intensity", True, TEXT_DIM)
    surface.blit(x_label, (graph_x + graph_w - 50, graph_y + graph_h + 8))
    
    y_label = font.render("Motor", True, TEXT_DIM)
    surface.blit(y_label, (x + 8, graph_y + graph_h // 2 - 10))
    y_label2 = font.render("Speed", True, TEXT_DIM)
    surface.blit(y_label2, (x + 8, graph_y + graph_h // 2 + 5))
    
    # Draw optimal intensity marker for Gaussian
    optimal = vehicle_gaussian.optimal_intensity
    optimal_x = graph_x + int((optimal / 300) * graph_w)
    if graph_x < optimal_x < graph_x + graph_w:
        pygame.draw.line(surface, (80, 80, 80), (optimal_x, graph_y), 
                        (optimal_x, graph_y + graph_h), 1)
        opt_label = font.render("optimal", True, TEXT_DIM)
        surface.blit(opt_label, (optimal_x - 20, graph_y + graph_h + 8))
    
    # Draw Gaussian curve
    points_gaussian = []
    points_linear = []
    
    for i in range(graph_w):
        intensity = (i / graph_w) * 300  # 0 to 300 intensity range
        
        # Gaussian response
        diff = intensity - vehicle_gaussian.optimal_intensity
        gauss_response = math.exp(-(diff * diff) / (2 * vehicle_gaussian.curve_width ** 2))
        gy = graph_y + graph_h - int(gauss_response * graph_h * 0.9)
        points_gaussian.append((graph_x + i, gy))
        
        # Linear response
        lin_response = min(1.0, intensity * vehicle_linear.linear_slope * vehicle_linear.intensity_scale)
        ly = graph_y + graph_h - int(lin_response * graph_h * 0.9)
        points_linear.append((graph_x + i, ly))
    
    # Draw curves
    if len(points_linear) > 1:
        pygame.draw.lines(surface, ACCENT_ORANGE, False, points_linear, 2)
    if len(points_gaussian) > 1:
        pygame.draw.lines(surface, ACCENT_TEAL, False, points_gaussian, 2)
    
    # Current intensity markers
    avg_intensity_gauss = (vehicle_gaussian.left_intensity + vehicle_gaussian.right_intensity) / 2
    avg_intensity_lin = (vehicle_linear.left_intensity + vehicle_linear.right_intensity) / 2
    
    # Gaussian marker
    marker_x_g = graph_x + int((min(avg_intensity_gauss, 300) / 300) * graph_w)
    diff_g = avg_intensity_gauss - vehicle_gaussian.optimal_intensity
    response_g = math.exp(-(diff_g * diff_g) / (2 * vehicle_gaussian.curve_width ** 2))
    marker_y_g = graph_y + graph_h - int(response_g * graph_h * 0.9)
    if graph_x <= marker_x_g <= graph_x + graph_w:
        pygame.draw.circle(surface, ACCENT_TEAL, (marker_x_g, marker_y_g), 6)
        pygame.draw.circle(surface, (255, 255, 255), (marker_x_g, marker_y_g), 6, 2)
    
    # Linear marker
    marker_x_l = graph_x + int((min(avg_intensity_lin, 300) / 300) * graph_w)
    response_l = min(1.0, avg_intensity_lin * vehicle_linear.linear_slope * vehicle_linear.intensity_scale)
    marker_y_l = graph_y + graph_h - int(response_l * graph_h * 0.9)
    if graph_x <= marker_x_l <= graph_x + graph_w:
        pygame.draw.circle(surface, ACCENT_ORANGE, (marker_x_l, marker_y_l), 6)
        pygame.draw.circle(surface, (255, 255, 255), (marker_x_l, marker_y_l), 6, 2)
    
    # Legend
    pygame.draw.line(surface, ACCENT_TEAL, (x + width - 180, y + 12), (x + width - 150, y + 12), 3)
    legend1 = font.render("Gaussian (peaked)", True, ACCENT_TEAL)
    surface.blit(legend1, (x + width - 145, y + 6))
    
    pygame.draw.line(surface, ACCENT_ORANGE, (x + width - 180, y + 28), (x + width - 150, y + 28), 3)
    legend2 = font.render("Linear (monotonic)", True, ACCENT_ORANGE)
    surface.blit(legend2, (x + width - 145, y + 22))


def draw_info_panel(surface: pygame.Surface, x: int, y: int, width: int, height: int,
                    vehicle_gaussian: VehicleGaussian, vehicle_linear: VehicleLinear) -> None:
    """Draw real-time information panel."""
    pygame.draw.rect(surface, GRAPH_BG, (x, y, width, height))
    pygame.draw.rect(surface, DIVIDER_COLOR, (x, y, width, height), 2)
    
    # Gaussian stats
    title1 = font_medium.render("GAUSSIAN Vehicle 4a", True, ACCENT_TEAL)
    surface.blit(title1, (x + 10, y + 10))
    
    info1 = [
        f"Intensity L: {vehicle_gaussian.left_intensity:.1f}",
        f"Intensity R: {vehicle_gaussian.right_intensity:.1f}",
        f"Motor L: {vehicle_gaussian.left_motor_speed:.2f}",
        f"Motor R: {vehicle_gaussian.right_motor_speed:.2f}",
        f"Optimal: {vehicle_gaussian.optimal_intensity:.0f}",
    ]
    
    for i, text in enumerate(info1):
        txt = font.render(text, True, TEXT_DIM)
        surface.blit(txt, (x + 10, y + 32 + i * 16))
    
    # Linear stats
    title2 = font_medium.render("LINEAR Vehicle", True, ACCENT_ORANGE)
    surface.blit(title2, (x + width // 2 + 10, y + 10))
    
    info2 = [
        f"Intensity L: {vehicle_linear.left_intensity:.1f}",
        f"Intensity R: {vehicle_linear.right_intensity:.1f}",
        f"Motor L: {vehicle_linear.left_motor_speed:.2f}",
        f"Motor R: {vehicle_linear.right_motor_speed:.2f}",
        f"Slope: {vehicle_linear.linear_slope:.3f}",
    ]
    
    for i, text in enumerate(info2):
        txt = font.render(text, True, TEXT_DIM)
        surface.blit(txt, (x + width // 2 + 10, y + 32 + i * 16))


def main():
    # Create sources - one on each side at same relative position
    sources_left: List[Source] = [Source(WIDTH // 4, HEIGHT // 2 + 100)]
    sources_right: List[Source] = [Source(3 * WIDTH // 4, HEIGHT // 2 + 100)]
    
    # Create vehicles
    vehicle_gaussian = VehicleGaussian(WIDTH // 4 - 100, HEIGHT // 2 - 50, heading=0.5)
    vehicle_linear = VehicleLinear(3 * WIDTH // 4 - 100, HEIGHT // 2 - 50, heading=0.5)
    
    instructions = [
        "VEHICLE 4 COMPARISON: Non-Linear (Gaussian) vs Linear Response",
        "",
        "Left Side: GAUSSIAN - Motor peaks at optimal intensity, then DECREASES",
        "           Creates ORBITING behavior around the source",
        "",
        "Right Side: LINEAR - Motor always increases with intensity (monotonic)",
        "            Rushes toward source, may crash or oscillate wildly",
        "",
        "Controls: Click to add source | R = Reset | Q = Quit",
    ]
    
    running = True
    while running:
        screen.fill(BG_COLOR)
        
        # Draw center divider
        pygame.draw.line(screen, DIVIDER_COLOR, (WIDTH // 2, 170), (WIDTH // 2, HEIGHT), 2)
        
        # Section labels
        left_label = font_title.render("NON-LINEAR (Gaussian)", True, ACCENT_TEAL)
        screen.blit(left_label, (WIDTH // 4 - 100, 175))
        
        right_label = font_title.render("LINEAR (Monotonic)", True, ACCENT_ORANGE)
        screen.blit(right_label, (3 * WIDTH // 4 - 90, 175))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    sources_left = [Source(WIDTH // 4, HEIGHT // 2 + 100)]
                    sources_right = [Source(3 * WIDTH // 4, HEIGHT // 2 + 100)]
                    vehicle_gaussian = VehicleGaussian(WIDTH // 4 - 100, HEIGHT // 2 - 50, heading=0.5)
                    vehicle_linear = VehicleLinear(3 * WIDTH // 4 - 100, HEIGHT // 2 - 50, heading=0.5)
                elif event.key == pygame.K_q:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if my > 170:  # Below header area
                    if mx < WIDTH // 2:
                        sources_left.append(Source(mx, my))
                    else:
                        sources_right.append(Source(mx, my))
        
        # Draw sources
        for src in sources_left:
            src.draw(screen)
        for src in sources_right:
            src.draw(screen)
        
        # Update vehicles
        vehicle_gaussian.update(sources_left)
        vehicle_linear.update(sources_right)
        
        # Draw vehicles
        vehicle_gaussian.draw(screen)
        vehicle_linear.draw(screen)
        
        # Draw response function comparison graph (top center)
        draw_response_graph(screen, 150, 5, WIDTH - 300, 160, vehicle_gaussian, vehicle_linear)
        
        # Draw info panel
        draw_info_panel(screen, 5, 5, 140, 120, vehicle_gaussian, vehicle_linear)
        
        # Instructions (bottom)
        y_offset = HEIGHT - 100
        for i, line in enumerate(instructions[:3]):
            color = TEXT_PRIMARY if i == 0 else TEXT_DIM
            txt = font.render(line, True, color)
            screen.blit(txt, (10, y_offset + i * 14))
        
        pygame.display.flip()
        clock.tick(fps)
    
    pygame.quit()


if __name__ == "__main__":
    main()


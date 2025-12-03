import pygame
import math
from typing import List, Literal, Union
from enum import Enum

pygame.init()

# Setup Pygame window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 4 - Values and Special Tastes (Non-monotonic Connections)")

# Setup clock for controlling frame rate
clock = pygame.time.Clock()
fps = 60

# Setup font for labels
font = pygame.font.SysFont("consolas", 14)
font_large = pygame.font.SysFont("consolas", 16, bold=True)


class SourceType(Enum):
    """Different types of environmental stimuli."""
    LIGHT = "Light"
    SOUND = "Sound"
    SMELL = "Smell"
    HEAT = "Heat"


# Source class representing different environmental stimuli
class Source:
    def __init__(self, x: float, y: float, source_type: SourceType, radius: int = 20):
        self.x = x
        self.y = y
        self.source_type = source_type
        self.radius = radius
        
        # Color coding for different source types
        self.colors = {
            SourceType.LIGHT: (255, 255, 0),      # Yellow
            SourceType.SOUND: (100, 100, 255),    # Blue
            SourceType.SMELL: (200, 100, 200),    # Purple
            SourceType.HEAT: (255, 100, 50),      # Orange-red
        }

    def draw(self, surface: pygame.Surface) -> None:
        color = self.colors[self.source_type]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw label
        label = font.render(self.source_type.value, True, (0, 0, 0))
        surface.blit(label, (int(self.x) - 20, int(self.y) + self.radius + 5))


class VehicleFourA:
    """
    Vehicle 4a: Non-monotonic connections (peaked response curves)
    
    Motor speed has a MAXIMUM at a certain optimal intensity.
    Below optimal: motor speeds up as intensity increases (approaching)
    Above optimal: motor slows down as intensity increases (too close)
    
    This creates orbiting behavior around sources at the optimal distance.
    """
    def __init__(self, x: float, y: float, radius: int = 25, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius * 1.5
        self.sensor_angle = 0.7  # Angle between sensors
        
        self.base_speed = 1.0
        self.max_motor_boost = 2.0  # Maximum additional speed at optimal intensity
        
        # Optimal intensity for peak motor response (different for each source type)
        # At this intensity, motor runs fastest. Below or above, motor is slower.
        self.optimal_intensity = {
            SourceType.LIGHT: 150.0,   # Prefers medium-distance light
            SourceType.SOUND: 200.0,   # Prefers closer sound
            SourceType.SMELL: 100.0,   # Prefers weaker smell
            SourceType.HEAT: 80.0,     # Avoids strong heat
        }
        
        # Width of the bell curve (smaller = sharper peak)
        self.curve_width = {
            SourceType.LIGHT: 100.0,
            SourceType.SOUND: 120.0,
            SourceType.SMELL: 80.0,
            SourceType.HEAT: 60.0,
        }
        
        # Connection type: crossed or uncrossed
        self.connection_type = {
            SourceType.LIGHT: 'crossed',     # Approaches light (like 2b)
            SourceType.SOUND: 'uncrossed',   # Avoids sound initially (like 2a)
            SourceType.SMELL: 'crossed',     # Approaches smell
            SourceType.HEAT: 'uncrossed',    # Avoids heat
        }
        
        self.left_motor_speed = 0.0
        self.right_motor_speed = 0.0

    def _sensor_position(self, angle: float) -> tuple[float, float]:
        """Calculate world position of sensor given local angle."""
        sensor_local_x = math.cos(angle) * self.sensor_dist
        sensor_local_y = math.sin(angle) * self.sensor_dist
        cos_heading = math.cos(self.heading)
        sin_heading = math.sin(self.heading)
        sensor_world_x = self.x + cos_heading * sensor_local_x - sin_heading * sensor_local_y
        sensor_world_y = self.y + sin_heading * sensor_local_x + cos_heading * sensor_local_y
        return (sensor_world_x, sensor_world_y)

    def _intensity_one(self, point_x: float, point_y: float, source_x: float, source_y: float) -> float:
        """Calculate intensity from one source at a given point (inverse square law)."""
        dx = source_x - point_x
        dy = source_y - point_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 1.0:
            distance = 1.0
        # Inverse square law
        intensity = 50000.0 / (distance * distance)
        return intensity

    def _intensity_at(self, point_x: float, point_y: float, sources: List[Source], source_type: SourceType) -> float:
        """Calculate total intensity from all sources of a specific type at a given point."""
        return sum(
            self._intensity_one(point_x, point_y, source.x, source.y)
            for source in sources
            if source.source_type == source_type
        )

    def _bell_curve_response(self, intensity: float, optimal: float, width: float) -> float:
        """
        Non-monotonic response: bell curve centered at optimal intensity.
        Returns value between 0 and 1, with 1 at optimal intensity.
        """
        # Gaussian-like bell curve
        exponent = -((intensity - optimal) ** 2) / (2 * width * width)
        return math.exp(exponent)

    def update(self, sources: List[Source]) -> None:
        """Update vehicle with non-monotonic response curves."""
        left_motor = self.base_speed
        right_motor = self.base_speed

        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)

        # Process each source type with its non-monotonic response
        for source_type in SourceType:
            left_intensity = self._intensity_at(left_pos[0], left_pos[1], sources, source_type)
            right_intensity = self._intensity_at(right_pos[0], right_pos[1], sources, source_type)
            
            if left_intensity < 0.1 and right_intensity < 0.1:
                continue  # Skip if no sources of this type nearby
            
            optimal = self.optimal_intensity[source_type]
            width = self.curve_width[source_type]
            connection = self.connection_type[source_type]
            
            # Calculate bell curve response (peaks at optimal intensity)
            left_response = self._bell_curve_response(left_intensity, optimal, width)
            right_response = self._bell_curve_response(right_intensity, optimal, width)
            
            # Apply motor boost based on response (0 to max_motor_boost)
            left_boost = left_response * self.max_motor_boost
            right_boost = right_response * self.max_motor_boost
            
            if connection == 'uncrossed':
                # Same-side: left sensor -> left motor
                left_motor += left_boost
                right_motor += right_boost
            else:  # crossed
                # Opposite-side: left sensor -> right motor
                left_motor += right_boost
                right_motor += left_boost

        # Ensure motors don't go negative
        left_motor = max(0.0, left_motor)
        right_motor = max(0.0, right_motor)
        
        self.left_motor_speed = left_motor
        self.right_motor_speed = right_motor

        # Calculate forward speed and turning rate
        forward_speed = (left_motor + right_motor) / 2
        turning_rate = (left_motor - right_motor) / (self.radius * 1.5)

        # Update heading and position
        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)

        # Wrap around screen edges
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface: pygame.Surface) -> None:
        """Draw vehicle."""
        # Draw vehicle body as a teal circle
        pygame.draw.circle(surface, (0, 180, 180), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

        # Draw direction indicator
        arrow_len = self.radius * 1.5
        arrow_end_x = self.x + math.cos(self.heading) * arrow_len
        arrow_end_y = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(
            surface, 
            (255, 255, 255), 
            (int(self.x), int(self.y)), 
            (int(arrow_end_x), int(arrow_end_y)), 
            3
        )

        # Draw sensors
        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)
        pygame.draw.circle(surface, (255, 0, 0), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 0, 0), (int(right_pos[0]), int(right_pos[1])), 5)

        # Draw label
        label_text = font_large.render("Vehicle 4a", True, (0, 0, 0))
        surface.blit(label_text, (int(self.x) - 35, int(self.y) - self.radius - 20))
        
        # Draw motor speed bars
        bar_height = 30
        bar_width = 5
        max_display_speed = 4.0
        left_bar_length = min(bar_height, (self.left_motor_speed / max_display_speed) * bar_height)
        right_bar_length = min(bar_height, (self.right_motor_speed / max_display_speed) * bar_height)
        
        left_bar_x = int(self.x) - self.radius - 10
        left_bar_y = int(self.y) - int(left_bar_length / 2)
        pygame.draw.rect(surface, (0, 255, 0), (left_bar_x, left_bar_y, bar_width, int(left_bar_length)))
        
        right_bar_x = int(self.x) + self.radius + 5
        right_bar_y = int(self.y) - int(right_bar_length / 2)
        pygame.draw.rect(surface, (0, 255, 0), (right_bar_x, right_bar_y, bar_width, int(right_bar_length)))


class VehicleFourB:
    """
    Vehicle 4b: Threshold-based connections with abrupt changes.
    
    Motor doesn't activate until stimulus reaches a threshold.
    Beyond threshold, motor jumps to a minimum activation, then increases.
    Creates "decision-like" behavior with deliberation before action.
    """
    def __init__(self, x: float, y: float, radius: int = 25, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius * 1.5
        self.sensor_angle = 0.7
        
        self.base_speed = 0.8
        
        # Threshold and jump values for each source type
        self.threshold = {
            SourceType.LIGHT: 50.0,
            SourceType.SOUND: 80.0,
            SourceType.SMELL: 40.0,
            SourceType.HEAT: 60.0,
        }
        
        # Minimum motor speed when threshold is exceeded
        self.min_activation = {
            SourceType.LIGHT: 1.5,
            SourceType.SOUND: 1.2,
            SourceType.SMELL: 1.0,
            SourceType.HEAT: 1.8,
        }
        
        # Slope after threshold (how much motor speed increases per intensity unit)
        self.slope = {
            SourceType.LIGHT: 0.015,
            SourceType.SOUND: 0.012,
            SourceType.SMELL: 0.010,
            SourceType.HEAT: 0.020,
        }
        
        self.connection_type = {
            SourceType.LIGHT: 'crossed',     # Approaches
            SourceType.SOUND: 'uncrossed',   # Avoids
            SourceType.SMELL: 'crossed',     # Approaches
            SourceType.HEAT: 'uncrossed',    # Avoids
        }
        
        self.left_motor_speed = 0.0
        self.right_motor_speed = 0.0

    def _sensor_position(self, angle: float) -> tuple[float, float]:
        sensor_local_x = math.cos(angle) * self.sensor_dist
        sensor_local_y = math.sin(angle) * self.sensor_dist
        cos_heading = math.cos(self.heading)
        sin_heading = math.sin(self.heading)
        sensor_world_x = self.x + cos_heading * sensor_local_x - sin_heading * sensor_local_y
        sensor_world_y = self.y + sin_heading * sensor_local_x + cos_heading * sensor_local_y
        return (sensor_world_x, sensor_world_y)

    def _intensity_one(self, point_x: float, point_y: float, source_x: float, source_y: float) -> float:
        dx = source_x - point_x
        dy = source_y - point_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 1.0:
            distance = 1.0
        intensity = 50000.0 / (distance * distance)
        return intensity

    def _intensity_at(self, point_x: float, point_y: float, sources: List[Source], source_type: SourceType) -> float:
        return sum(
            self._intensity_one(point_x, point_y, source.x, source.y)
            for source in sources
            if source.source_type == source_type
        )

    def _threshold_response(self, intensity: float, threshold: float, min_activation: float, slope: float) -> float:
        """
        Step-function response with threshold.
        Below threshold: returns 0
        At/above threshold: jumps to min_activation, then increases linearly
        """
        if intensity < threshold:
            return 0.0
        else:
            # Jump to minimum activation, then increase with slope
            return min_activation + (intensity - threshold) * slope

    def update(self, sources: List[Source]) -> None:
        """Update vehicle with threshold-based response."""
        left_motor = self.base_speed
        right_motor = self.base_speed

        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)

        for source_type in SourceType:
            left_intensity = self._intensity_at(left_pos[0], left_pos[1], sources, source_type)
            right_intensity = self._intensity_at(right_pos[0], right_pos[1], sources, source_type)
            
            threshold = self.threshold[source_type]
            min_act = self.min_activation[source_type]
            slp = self.slope[source_type]
            connection = self.connection_type[source_type]
            
            left_response = self._threshold_response(left_intensity, threshold, min_act, slp)
            right_response = self._threshold_response(right_intensity, threshold, min_act, slp)
            
            if connection == 'uncrossed':
                left_motor += left_response
                right_motor += right_response
            else:
                left_motor += right_response
                right_motor += left_response

        left_motor = max(0.0, left_motor)
        right_motor = max(0.0, right_motor)
        
        self.left_motor_speed = left_motor
        self.right_motor_speed = right_motor

        forward_speed = (left_motor + right_motor) / 2
        turning_rate = (left_motor - right_motor) / (self.radius * 1.5)

        self.heading += turning_rate
        self.x += forward_speed * math.cos(self.heading)
        self.y += forward_speed * math.sin(self.heading)

        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface: pygame.Surface) -> None:
        # Draw vehicle body as an orange circle
        pygame.draw.circle(surface, (255, 140, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

        arrow_len = self.radius * 1.5
        arrow_end_x = self.x + math.cos(self.heading) * arrow_len
        arrow_end_y = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(
            surface, 
            (255, 255, 255), 
            (int(self.x), int(self.y)), 
            (int(arrow_end_x), int(arrow_end_y)), 
            3
        )

        left_pos = self._sensor_position(-self.sensor_angle)
        right_pos = self._sensor_position(self.sensor_angle)
        pygame.draw.circle(surface, (255, 0, 0), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 0, 0), (int(right_pos[0]), int(right_pos[1])), 5)

        label_text = font_large.render("Vehicle 4b", True, (0, 0, 0))
        surface.blit(label_text, (int(self.x) - 35, int(self.y) - self.radius - 20))
        
        bar_height = 30
        bar_width = 5
        max_display_speed = 5.0
        left_bar_length = min(bar_height, (self.left_motor_speed / max_display_speed) * bar_height)
        right_bar_length = min(bar_height, (self.right_motor_speed / max_display_speed) * bar_height)
        
        left_bar_x = int(self.x) - self.radius - 10
        left_bar_y = int(self.y) - int(left_bar_length / 2)
        pygame.draw.rect(surface, (0, 200, 255), (left_bar_x, left_bar_y, bar_width, int(left_bar_length)))
        
        right_bar_x = int(self.x) + self.radius + 5
        right_bar_y = int(self.y) - int(right_bar_length / 2)
        pygame.draw.rect(surface, (0, 200, 255), (right_bar_x, right_bar_y, bar_width, int(right_bar_length)))


# Vehicle type selection
VehicleType = Literal['4a', '4b']


def create_initial_sources() -> List[Source]:
    """Create empty source list (clean board)."""
    return []


def create_vehicle(vehicle_type: VehicleType) -> Union[VehicleFourA, VehicleFourB]:
    """Create a vehicle at the center."""
    if vehicle_type == '4a':
        return VehicleFourA(WIDTH // 2, HEIGHT // 2, heading=0)
    else:
        return VehicleFourB(WIDTH // 2, HEIGHT // 2, heading=0)


# Create initial state
sources: List[Source] = create_initial_sources()
current_vehicle_type: VehicleType = '4a'
vehicle = create_vehicle(current_vehicle_type)

# Instructions text
instructions = [
    "Vehicle 4: Non-monotonic and Threshold Connections",
    "",
    "Vehicle 4a (teal): Peaked response - orbits at optimal distance",
    "Vehicle 4b (orange): Threshold response - deliberates then acts",
    "",
    "Sources: 1=Light, 2=Sound, 3=Smell, 4=Heat",
    "Toggle: A=Vehicle 4a, B=Vehicle 4b",
    "Click to add sources | R=Reset board"
]

current_source_type = SourceType.LIGHT

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_source_type = SourceType.LIGHT
            elif event.key == pygame.K_2:
                current_source_type = SourceType.SOUND
            elif event.key == pygame.K_3:
                current_source_type = SourceType.SMELL
            elif event.key == pygame.K_4:
                current_source_type = SourceType.HEAT
            elif event.key == pygame.K_a:
                current_vehicle_type = '4a'
                vehicle = create_vehicle(current_vehicle_type)
            elif event.key == pygame.K_b:
                current_vehicle_type = '4b'
                vehicle = create_vehicle(current_vehicle_type)
            elif event.key == pygame.K_r:
                sources = create_initial_sources()
                vehicle = create_vehicle(current_vehicle_type)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            sources.append(Source(event.pos[0], event.pos[1], current_source_type))

    # Draw all sources
    for source in sources:
        source.draw(screen)

    # Update and draw vehicle
    vehicle.update(sources)
    vehicle.draw(screen)

    # Draw instructions
    y_offset = 10
    for instruction in instructions:
        text_surface = font.render(instruction, True, (50, 50, 50))
        screen.blit(text_surface, (10, y_offset))
        y_offset += 18

    # Show current source type and vehicle type
    current_type_text = font_large.render(
        f"Source: {current_source_type.value} | Vehicle: {current_vehicle_type}", 
        True, 
        (0, 0, 0)
    )
    screen.blit(current_type_text, (WIDTH - 300, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()


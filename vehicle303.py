import pygame
import math
from typing import List, Literal
from enum import Enum

pygame.init()

# Setup Pygame window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 3 - All Variants (3a Love, 3b Explorer, 3c Multi-sensorial)")

# Setup clock for controlling frame rate
clock = pygame.time.Clock()
fps = 60

# Setup font for labels
font = pygame.font.SysFont("consolas", 14)
font_large = pygame.font.SysFont("consolas", 16, bold=True)


class SourceType(Enum):
    """Different types of environmental stimuli."""
    TEMPERATURE = "Temperature"
    LIGHT = "Light"
    OXYGEN = "Oxygen"
    ORGANIC = "Organic"


# Source class representing different environmental stimuli
class Source:
    def __init__(self, x: float, y: float, source_type: SourceType, radius: int = 20):
        self.x = x
        self.y = y
        self.source_type = source_type
        self.radius = radius
        
        # Color coding for different source types
        self.colors = {
            SourceType.TEMPERATURE: (255, 100, 50),   # Orange-red (hot)
            SourceType.LIGHT: (255, 255, 0),          # Yellow (bright)
            SourceType.OXYGEN: (100, 150, 255),       # Light blue (air)
            SourceType.ORGANIC: (100, 200, 100),      # Green (organic matter)
        }

    def draw(self, surface: pygame.Surface) -> None:
        color = self.colors[self.source_type]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw label
        label = font.render(self.source_type.value, True, (0, 0, 0))
        surface.blit(label, (int(self.x) - 30, int(self.y) + self.radius + 5))


# Vehicle 3a - Love: Uncrossed (straight) inhibitory connections
# Left sensor inhibits LEFT motor, Right sensor inhibits RIGHT motor
# Behavior: Slows down near source AND turns TOWARD it → approaches and rests FACING the source
class VehicleThreeA:
    """
    Vehicle 3a with uncrossed (straight) inhibitory connections.
    - Left sensor → inhibits Left motor (same side)
    - Right sensor → inhibits Right motor (same side)
    Behavior: "LOVE" - approaches source, slows down, comes to rest FACING the source.
    From the book: "staying close by in quiet admiration"
    """
    def __init__(self, x: float, y: float, radius: int = 25, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius * 1.5
        self.left_motor_speed = 0.0
        self.right_motor_speed = 0.0
        
        self.sensor_angle = 0.7  # Angle from heading for left/right sensors
        self.base_speed = 2.0
        self.inhibitory_scale = 0.12

    def _sensor_position(self, side: Literal["left", "right"]) -> tuple[float, float]:
        """Calculate world position of sensor."""
        angle_offset = -self.sensor_angle if side == "left" else self.sensor_angle
        sensor_local_x = math.cos(angle_offset) * self.sensor_dist
        sensor_local_y = math.sin(angle_offset) * self.sensor_dist
        cos_heading = math.cos(self.heading)
        sin_heading = math.sin(self.heading)
        sensor_world_x = self.x + cos_heading * sensor_local_x - sin_heading * sensor_local_y
        sensor_world_y = self.y + sin_heading * sensor_local_x + cos_heading * sensor_local_y
        return (sensor_world_x, sensor_world_y)

    def _intensity_at(self, point_x: float, point_y: float, sources: List[Source]) -> float:
        """Calculate total intensity from all sources at a given point."""
        total = 0.0
        for source in sources:
            dx = source.x - point_x
            dy = source.y - point_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 0.5:
                distance = 0.5
            total += 50000.0 / (distance * distance)
        return total

    def update(self, sources: List[Source]) -> None:
        """Update vehicle with uncrossed (straight) inhibitory connections."""
        left_pos = self._sensor_position("left")
        right_pos = self._sensor_position("right")
        
        left_intensity = self._intensity_at(left_pos[0], left_pos[1], sources)
        right_intensity = self._intensity_at(right_pos[0], right_pos[1], sources)

        # UNCROSSED (straight) inhibitory: left sensor → left motor, right sensor → right motor
        # When source is on left: left sensor stronger → left motor slows more → turns LEFT toward source
        left_motor = self.base_speed - left_intensity * self.inhibitory_scale
        right_motor = self.base_speed - right_intensity * self.inhibitory_scale

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
        """Draw vehicle with pink color for 3a Love variant."""
        # Body - pink (love color)
        pygame.draw.circle(surface, (255, 100, 150), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

        # Direction indicator
        arrow_len = self.radius * 1.5
        arrow_end_x = self.x + math.cos(self.heading) * arrow_len
        arrow_end_y = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(surface, (255, 255, 255), 
                        (int(self.x), int(self.y)), 
                        (int(arrow_end_x), int(arrow_end_y)), 3)

        # Sensor positions
        left_pos = self._sensor_position("left")
        right_pos = self._sensor_position("right")
        pygame.draw.circle(surface, (255, 0, 0), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 0, 0), (int(right_pos[0]), int(right_pos[1])), 5)

        # Label
        label_text = font_large.render("3a Love", True, (0, 0, 0))
        surface.blit(label_text, (int(self.x) - 30, int(self.y) - self.radius - 20))
        
        # Motor bars
        bar_height = 30
        bar_width = 5
        max_speed = 3.0
        left_bar_len = min(bar_height, (self.left_motor_speed / max_speed) * bar_height)
        right_bar_len = min(bar_height, (self.right_motor_speed / max_speed) * bar_height)
        
        pygame.draw.rect(surface, (0, 255, 0), 
                        (int(self.x) - self.radius - 10, int(self.y) - int(left_bar_len / 2), 
                         bar_width, int(left_bar_len)))
        pygame.draw.rect(surface, (0, 255, 0), 
                        (int(self.x) + self.radius + 5, int(self.y) - int(right_bar_len / 2), 
                         bar_width, int(right_bar_len)))


# Vehicle 3b - Explorer: Crossed inhibitory connections
# Left sensor inhibits RIGHT motor, Right sensor inhibits LEFT motor
# Behavior: Slows down near source but turns AWAY from it → orbits/explores around source
class VehicleThreeB:
    """
    Vehicle 3b with crossed inhibitory connections.
    - Left sensor → inhibits Right motor (opposite side)
    - Right sensor → inhibits Left motor (opposite side)
    Behavior: "EXPLORER" - attracted to source (slows down) but faces AWAY from it.
    From the book: "keeps an eye open for other, perhaps stronger sources"
    May drift away due to slight perturbations since it faces away from source.
    """
    def __init__(self, x: float, y: float, radius: int = 25, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius * 1.5
        self.left_motor_speed = 0.0
        self.right_motor_speed = 0.0
        
        self.sensor_angle = 0.7
        self.base_speed = 2.0
        self.inhibitory_scale = 0.12

    def _sensor_position(self, side: Literal["left", "right"]) -> tuple[float, float]:
        """Calculate world position of sensor."""
        angle_offset = -self.sensor_angle if side == "left" else self.sensor_angle
        sensor_local_x = math.cos(angle_offset) * self.sensor_dist
        sensor_local_y = math.sin(angle_offset) * self.sensor_dist
        cos_heading = math.cos(self.heading)
        sin_heading = math.sin(self.heading)
        sensor_world_x = self.x + cos_heading * sensor_local_x - sin_heading * sensor_local_y
        sensor_world_y = self.y + sin_heading * sensor_local_x + cos_heading * sensor_local_y
        return (sensor_world_x, sensor_world_y)

    def _intensity_at(self, point_x: float, point_y: float, sources: List[Source]) -> float:
        """Calculate total intensity from all sources at a given point."""
        total = 0.0
        for source in sources:
            dx = source.x - point_x
            dy = source.y - point_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 0.5:
                distance = 0.5
            total += 50000.0 / (distance * distance)
        return total

    def update(self, sources: List[Source]) -> None:
        """Update vehicle with crossed inhibitory connections."""
        left_pos = self._sensor_position("left")
        right_pos = self._sensor_position("right")
        
        left_intensity = self._intensity_at(left_pos[0], left_pos[1], sources)
        right_intensity = self._intensity_at(right_pos[0], right_pos[1], sources)

        # CROSSED inhibitory: left sensor → right motor, right sensor → left motor
        # When source is on left: left sensor stronger → right motor slows more → turns RIGHT away from source
        left_motor = self.base_speed - right_intensity * self.inhibitory_scale
        right_motor = self.base_speed - left_intensity * self.inhibitory_scale

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
        """Draw vehicle with cyan color for 3b Explorer variant."""
        # Body - cyan (explorer color)
        pygame.draw.circle(surface, (0, 200, 200), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

        # Direction indicator
        arrow_len = self.radius * 1.5
        arrow_end_x = self.x + math.cos(self.heading) * arrow_len
        arrow_end_y = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(surface, (255, 255, 255), 
                        (int(self.x), int(self.y)), 
                        (int(arrow_end_x), int(arrow_end_y)), 3)

        # Sensor positions
        left_pos = self._sensor_position("left")
        right_pos = self._sensor_position("right")
        pygame.draw.circle(surface, (255, 0, 0), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 0, 0), (int(right_pos[0]), int(right_pos[1])), 5)

        # Label
        label_text = font_large.render("3b Explorer", True, (0, 0, 0))
        surface.blit(label_text, (int(self.x) - 40, int(self.y) - self.radius - 20))
        
        # Motor bars
        bar_height = 30
        bar_width = 5
        max_speed = 3.0
        left_bar_len = min(bar_height, (self.left_motor_speed / max_speed) * bar_height)
        right_bar_len = min(bar_height, (self.right_motor_speed / max_speed) * bar_height)
        
        pygame.draw.rect(surface, (0, 255, 0), 
                        (int(self.x) - self.radius - 10, int(self.y) - int(left_bar_len / 2), 
                         bar_width, int(left_bar_len)))
        pygame.draw.rect(surface, (0, 255, 0), 
                        (int(self.x) + self.radius + 5, int(self.y) - int(right_bar_len / 2), 
                         bar_width, int(right_bar_len)))


# Vehicle 3c class with multiple sensor pairs (multi-sensorial)
class VehicleThreeC:
    """
    Vehicle 3c with 4 sensor pairs tuned to different environmental qualities:
    - Pair 1 (Temperature): Uncrossed excitatory → AVOIDS/FEARS hot places
    - Pair 2 (Light): Crossed excitatory → AGGRESSION toward light (destroys them)
    - Pair 3 (Organic): Uncrossed inhibitory → LOVES organic matter (stays near)
    - Pair 4 (Oxygen): Crossed inhibitory → EXPLORES oxygen (likes but faces away)
    """
    def __init__(self, x: float, y: float, radius: int = 25, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = self.radius * 1.5
        self.left_motor_speed = 0.0  # For debug visualization
        self.right_motor_speed = 0.0  # For debug visualization
        
        # Four sensor pairs at wider angles for stronger differential response
        self.sensor_angles = [
            (-0.7, 0.7),   # Pair 1: Temperature sensors (wider angle)
            (-0.7, 0.7),   # Pair 2: Light sensors (wider angle)
            (-0.7, 0.7),   # Pair 3: Organic matter sensors (wider angle)
            (-0.7, 0.7),   # Pair 4: Oxygen sensors (wider angle)
        ]
        
        self.base_speed = 1.5
        # Stronger scales to ensure behaviors are distinct and not canceled out
        # Excitatory: speeds up when stimulus detected (avoidance/aggression)
        # Inhibitory: slows down when stimulus detected (attraction) - must be strong enough to allow resting
        self.excitatory_scale = 0.100   # For pairs 1 and 2 (avoidance and aggression)
        self.inhibitory_scale = 0.150   # For pairs 3 and 4 (attraction - strong enough to cause resting)

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
        """Calculate intensity from one source at a given point."""
        dx = source_x - point_x
        dy = source_y - point_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 0.5:
            distance = 0.5  # Prevent division by zero but allow strong signal at close range
        # Inverse square law - stronger at close range to allow resting behavior
        # At distance 10: intensity ~500, at distance 1: intensity ~50000
        intensity = 50000.0 / (distance * distance)
        return intensity

    def _intensity_at(self, point_x: float, point_y: float, sources: List[Source], source_type: SourceType) -> float:
        """Calculate total intensity from all sources of a specific type at a given point."""
        return sum(
            self._intensity_one(point_x, point_y, source.x, source.y)
            for source in sources
            if source.source_type == source_type
        )

    def update(self, sources: List[Source]) -> None:
        """Update vehicle using combined influence from all 4 sensor pairs."""
        left_motor = self.base_speed
        right_motor = self.base_speed

        # Process all 4 sensor pairs, each tuned to a different source type
        sensor_configs = [
            (0, SourceType.TEMPERATURE, 'excitatory', 'uncrossed'),  # Fear/avoidance
            (1, SourceType.LIGHT, 'excitatory', 'crossed'),          # Aggression
            (2, SourceType.ORGANIC, 'inhibitory', 'uncrossed'),      # Love
            (3, SourceType.OXYGEN, 'inhibitory', 'crossed'),         # Explorer
        ]

        for pair_idx, source_type, connection_type, crossing in sensor_configs:
            left_angle, right_angle = self.sensor_angles[pair_idx]
            left_pos = self._sensor_position(left_angle)
            right_pos = self._sensor_position(right_angle)
            
            # Each sensor pair only responds to its specific source type
            left_intensity = self._intensity_at(left_pos[0], left_pos[1], sources, source_type)
            right_intensity = self._intensity_at(right_pos[0], right_pos[1], sources, source_type)

            if connection_type == 'excitatory':
                scale = self.excitatory_scale
                if crossing == 'uncrossed':
                    # Same-side: left sensor → left motor, right sensor → right motor
                    left_motor += left_intensity * scale
                    right_motor += right_intensity * scale
                else:  # crossed
                    # Opposite-side: left sensor → right motor, right sensor → left motor
                    left_motor += right_intensity * scale
                    right_motor += left_intensity * scale
            else:  # inhibitory
                scale = self.inhibitory_scale
                if crossing == 'uncrossed':
                    # Same-side inhibition
                    left_motor -= left_intensity * scale
                    right_motor -= right_intensity * scale
                else:  # crossed
                    # Opposite-side inhibition
                    left_motor -= right_intensity * scale
                    right_motor -= left_intensity * scale

        # Ensure motors don't go negative (but can get very slow for resting behavior)
        # For inhibitory connections, vehicle should be able to come to rest (near zero speed)
        # According to the book: "They will actually come to rest in the immediate vicinity of the source"
        left_motor = max(0.0, left_motor)  # Allow complete rest (zero speed)
        right_motor = max(0.0, right_motor)
        
        # Store motor speeds for debug visualization
        self.left_motor_speed = left_motor
        self.right_motor_speed = right_motor

        # Calculate forward speed and turning rate
        # IMPORTANT: In differential drive, faster RIGHT wheel = turn LEFT
        # So turning_rate = (left - right): if left > right, vehicle turns right
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
        """Draw vehicle with distinct appearance for 3c variant."""
        # Draw vehicle body as a purple circle
        pygame.draw.circle(surface, (150, 0, 200), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

        # Draw direction indicator (white arrow)
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

        # Draw sensor positions
        left_pos = self._sensor_position(-0.7)
        right_pos = self._sensor_position(0.7)
        pygame.draw.circle(surface, (255, 0, 0), (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (255, 0, 0), (int(right_pos[0]), int(right_pos[1])), 5)

        # Draw label
        label_text = font_large.render("Vehicle 3c", True, (0, 0, 0))
        surface.blit(label_text, (int(self.x) - 35, int(self.y) - self.radius - 20))
        
        # Draw motor speed indicators as bars
        bar_height = 30
        bar_width = 5
        max_display_speed = 3.0  # Maximum speed for visualization scaling
        left_bar_length = min(bar_height, (self.left_motor_speed / max_display_speed) * bar_height)
        right_bar_length = min(bar_height, (self.right_motor_speed / max_display_speed) * bar_height)
        
        # Left motor bar (green)
        left_bar_x = int(self.x) - self.radius - 10
        left_bar_y = int(self.y) - int(left_bar_length / 2)
        pygame.draw.rect(surface, (0, 255, 0), (left_bar_x, left_bar_y, bar_width, int(left_bar_length)))
        
        # Right motor bar (green)
        right_bar_x = int(self.x) + self.radius + 5
        right_bar_y = int(self.y) - int(right_bar_length / 2)
        pygame.draw.rect(surface, (0, 255, 0), (right_bar_x, right_bar_y, bar_width, int(right_bar_length)))


# Initial setup function for reset
def create_initial_sources() -> List[Source]:
    """Create the initial set of sources (empty - user adds manually)."""
    return []  # Clean board - add sources yourself with mouse clicks

def create_vehicles() -> dict:
    """Create all three vehicle variants at different starting positions."""
    return {
        'a': VehicleThreeA(200, HEIGHT // 2, heading=0),        # Left side - cyan
        'b': VehicleThreeB(WIDTH // 2, HEIGHT // 2, heading=0), # Center - pink
        'c': VehicleThreeC(600, HEIGHT // 2, heading=0),        # Right side - purple
    }

# Create initial sources and vehicles
sources = create_initial_sources()
vehicles = create_vehicles()

# Instructions text
instructions = [
    "VEHICLE 3 VARIANTS - Inhibitory Connections",
    "",
    "3a (Pink) LOVE: Uncrossed inhibitory - approaches and rests FACING source",
    "3b (Cyan) EXPLORER: Crossed inhibitory - slows near source but faces AWAY",
    "3c (Purple) MULTI-SENSORIAL: responds to 4 different stimuli",
    "",
    "3c responds to: 1=Temp(avoid) 2=Light(aggro) 3=Organic(love) 4=O2(explore)",
    "",
    "Click to add sources | R=Reset | Press 1-4 to change source type"
]

# Track current source type for mouse clicks
current_source_type = SourceType.TEMPERATURE
source_type_list = [SourceType.TEMPERATURE, SourceType.LIGHT, SourceType.ORGANIC, SourceType.OXYGEN]

running = True
while running:
    screen.fill((255, 255, 255))  # White background

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Switch source type with number keys
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_source_type = SourceType.TEMPERATURE
            elif event.key == pygame.K_2:
                current_source_type = SourceType.LIGHT
            elif event.key == pygame.K_3:
                current_source_type = SourceType.ORGANIC
            elif event.key == pygame.K_4:
                current_source_type = SourceType.OXYGEN
            elif event.key == pygame.K_r:
                # Reset board
                sources = create_initial_sources()
                vehicles = create_vehicles()
        # Add new source on mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            sources.append(Source(event.pos[0], event.pos[1], current_source_type))

    # Draw all sources
    for source in sources:
        source.draw(screen)

    # Update and draw all vehicles
    for vehicle in vehicles.values():
        vehicle.update(sources)
        vehicle.draw(screen)

    # Draw instructions
    y_offset = 10
    for instruction in instructions:
        text_surface = font.render(instruction, True, (50, 50, 50))
        screen.blit(text_surface, (10, y_offset))
        y_offset += 18

    # Show current selected source type
    current_type_text = font_large.render(
        f"Current: {current_source_type.value} (press 1-4 to change)", 
        True, 
        (0, 0, 0)
    )
    screen.blit(current_type_text, (WIDTH - 380, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()

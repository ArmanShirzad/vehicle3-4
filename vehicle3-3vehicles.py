"""
Vehicle 3 Simulation - Three Vehicle Variants
Based on Braitenberg's Vehicles - Chapter 3

Vehicle 3a: Inhibitory Uncrossed → LOVES (faces source, stays in quiet admiration)
Vehicle 3b: Inhibitory Crossed → EXPLORER (faces away, seeks other sources)
Vehicle 3c: Multi-sensorial with 4 sensor pairs → VALUES and KNOWLEDGE
"""

import pygame
import math
from typing import List, Tuple
from enum import Enum
from abc import ABC, abstractmethod


pygame.init()

# Display Configuration
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vehicle 3 - Love, Exploration, and Knowledge")

clock = pygame.time.Clock()
FPS = 60

# Typography
font = pygame.font.SysFont("consolas", 13)
font_bold = pygame.font.SysFont("consolas", 14, bold=True)


class SourceType(Enum):
    """Environmental stimulus types for multi-sensorial vehicle."""
    GENERIC = "Source"         # For 3a and 3b (single type)
    TEMPERATURE = "Temperature"
    LIGHT = "Light"
    OXYGEN = "Oxygen"
    ORGANIC = "Organic"


class Source:
    """Environmental stimulus source."""
    
    COLORS = {
        SourceType.GENERIC: (200, 200, 200),       # Grey
        SourceType.TEMPERATURE: (255, 100, 50),    # Orange-red
        SourceType.LIGHT: (255, 230, 80),          # Yellow
        SourceType.OXYGEN: (100, 160, 255),        # Light blue
        SourceType.ORGANIC: (80, 180, 80),         # Green
    }
    
    def __init__(self, x: float, y: float, source_type: SourceType, radius: int = 18):
        self.x = x
        self.y = y
        self.source_type = source_type
        self.radius = radius

    def draw(self, surface: pygame.Surface) -> None:
        color = self.COLORS[self.source_type]
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (30, 30, 30), (int(self.x), int(self.y)), self.radius, 2)
        
        label = font.render(self.source_type.value, True, (30, 30, 30))
        label_x = int(self.x) - label.get_width() // 2
        surface.blit(label, (label_x, int(self.y) + self.radius + 4))


class VehicleBase(ABC):
    """Abstract base class for all Vehicle 3 variants."""
    
    def __init__(self, x: float, y: float, radius: int = 22, heading: float = 0):
        self.x = x
        self.y = y
        self.radius = radius
        self.heading = heading
        self.sensor_dist = radius * 1.4
        self.sensor_angle = 0.6  # Radians from center
        
        self.base_speed = 1.8
        self.left_motor = 0.0
        self.right_motor = 0.0
    
    def _sensor_position(self, angle_offset: float) -> Tuple[float, float]:
        """Calculate world position of sensor given local angle offset."""
        local_x = math.cos(angle_offset) * self.sensor_dist
        local_y = math.sin(angle_offset) * self.sensor_dist
        cos_h = math.cos(self.heading)
        sin_h = math.sin(self.heading)
        world_x = self.x + cos_h * local_x - sin_h * local_y
        world_y = self.y + sin_h * local_x + cos_h * local_y
        return (world_x, world_y)
    
    @property
    def left_sensor_pos(self) -> Tuple[float, float]:
        return self._sensor_position(-self.sensor_angle)
    
    @property
    def right_sensor_pos(self) -> Tuple[float, float]:
        return self._sensor_position(self.sensor_angle)
    
    def _intensity_from_source(self, sensor_pos: Tuple[float, float], 
                                source: Source) -> float:
        """Calculate intensity at sensor position from a single source."""
        dx = source.x - sensor_pos[0]
        dy = source.y - sensor_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        distance = max(distance, 1.0)  # Prevent division by zero
        return 40000.0 / (distance * distance)  # Inverse square law
    
    def _total_intensity(self, sensor_pos: Tuple[float, float], 
                         sources: List[Source], 
                         source_type: SourceType = None) -> float:
        """Calculate total intensity at sensor from all matching sources."""
        total = 0.0
        for source in sources:
            if source_type is None or source.source_type == source_type:
                total += self._intensity_from_source(sensor_pos, source)
        return total
    
    @abstractmethod
    def update(self, sources: List[Source]) -> None:
        """Update vehicle state based on sources. Must be implemented by subclass."""
        pass
    
    def _apply_motion(self) -> None:
        """Apply motor speeds to update position and heading."""
        # Clamp motors (inhibitory can reduce to zero but not negative)
        self.left_motor = max(0.0, self.left_motor)
        self.right_motor = max(0.0, self.right_motor)
        
        # Differential drive kinematics
        forward = (self.left_motor + self.right_motor) / 2
        turn_rate = (self.left_motor - self.right_motor) / (self.radius * 1.5)
        
        self.heading += turn_rate
        self.x += forward * math.cos(self.heading)
        self.y += forward * math.sin(self.heading)
        
        # Wrap around screen
        self.x %= WIDTH
        self.y %= HEIGHT
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the vehicle. Must be implemented by subclass."""
        pass
    
    def _draw_body(self, surface: pygame.Surface, color: Tuple[int, int, int], 
                   label: str) -> None:
        """Draw common vehicle body elements."""
        # Body circle
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (20, 20, 20), (int(self.x), int(self.y)), 
                          self.radius, 2)
        
        # Direction indicator
        arrow_len = self.radius * 1.4
        end_x = self.x + math.cos(self.heading) * arrow_len
        end_y = self.y + math.sin(self.heading) * arrow_len
        pygame.draw.line(surface, (255, 255, 255), 
                        (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), 3)
        
        # Sensors
        left_pos = self.left_sensor_pos
        right_pos = self.right_sensor_pos
        pygame.draw.circle(surface, (200, 50, 50), 
                          (int(left_pos[0]), int(left_pos[1])), 5)
        pygame.draw.circle(surface, (200, 50, 50), 
                          (int(right_pos[0]), int(right_pos[1])), 5)
        
        # Label
        text = font_bold.render(label, True, (20, 20, 20))
        surface.blit(text, (int(self.x) - text.get_width() // 2, 
                           int(self.y) - self.radius - 18))
    
    def _draw_motor_bars(self, surface: pygame.Surface) -> None:
        """Draw motor speed indicator bars."""
        bar_h = 25
        bar_w = 4
        max_speed = 3.0
        
        left_len = min(bar_h, (self.left_motor / max_speed) * bar_h)
        right_len = min(bar_h, (self.right_motor / max_speed) * bar_h)
        
        # Left bar
        lx = int(self.x) - self.radius - 8
        ly = int(self.y) - int(left_len / 2)
        pygame.draw.rect(surface, (50, 200, 50), (lx, ly, bar_w, int(left_len)))
        
        # Right bar
        rx = int(self.x) + self.radius + 4
        ry = int(self.y) - int(right_len / 2)
        pygame.draw.rect(surface, (50, 200, 50), (rx, ry, bar_w, int(right_len)))


class VehicleThreeA(VehicleBase):
    """
    Vehicle 3a: Inhibitory Uncrossed Connections
    
    Behavior: LOVES the source
    - Sensors inhibit same-side motors (left sensor -> left motor)
    - Turns TOWARD source (nearer sensor slows same-side motor)
    - Comes to rest FACING the source in quiet admiration
    """
    
    INHIBITORY_SCALE = 0.12
    
    def __init__(self, x: float, y: float, heading: float = 0):
        super().__init__(x, y, heading=heading)
    
    def update(self, sources: List[Source]) -> None:
        # Only respond to GENERIC sources
        left_intensity = self._total_intensity(self.left_sensor_pos, sources, 
                                               SourceType.GENERIC)
        right_intensity = self._total_intensity(self.right_sensor_pos, sources, 
                                                SourceType.GENERIC)
        
        # Inhibitory uncrossed: sensors slow down same-side motors
        self.left_motor = self.base_speed - left_intensity * self.INHIBITORY_SCALE
        self.right_motor = self.base_speed - right_intensity * self.INHIBITORY_SCALE
        
        self._apply_motion()
    
    def draw(self, surface: pygame.Surface) -> None:
        self._draw_body(surface, (70, 130, 180), "3a: LOVE")  # Steel blue
        self._draw_motor_bars(surface)


class VehicleThreeB(VehicleBase):
    """
    Vehicle 3b: Inhibitory Crossed Connections
    
    Behavior: EXPLORER
    - Sensors inhibit opposite-side motors (left sensor -> right motor)
    - Turns AWAY from source (nearer sensor slows opposite motor)
    - Comes to rest FACING AWAY from source
    - May drift away when perturbed, seeking other sources
    """
    
    INHIBITORY_SCALE = 0.12
    
    def __init__(self, x: float, y: float, heading: float = 0):
        super().__init__(x, y, heading=heading)
    
    def update(self, sources: List[Source]) -> None:
        # Only respond to GENERIC sources
        left_intensity = self._total_intensity(self.left_sensor_pos, sources, 
                                               SourceType.GENERIC)
        right_intensity = self._total_intensity(self.right_sensor_pos, sources, 
                                                SourceType.GENERIC)
        
        # Inhibitory crossed: sensors slow down opposite-side motors
        self.left_motor = self.base_speed - right_intensity * self.INHIBITORY_SCALE
        self.right_motor = self.base_speed - left_intensity * self.INHIBITORY_SCALE
        
        self._apply_motion()
    
    def draw(self, surface: pygame.Surface) -> None:
        self._draw_body(surface, (180, 130, 70), "3b: EXPLORER")  # Bronze
        self._draw_motor_bars(surface)


class VehicleThreeC(VehicleBase):
    """
    Vehicle 3c: Multi-sensorial with 4 sensor pairs
    
    Behavior: VALUES and KNOWLEDGE
    - Pair 1 (Temperature): Excitatory Uncrossed -> AVOIDS/FEARS (turns away + speeds up)
    - Pair 2 (Light): Excitatory Crossed -> AGGRESSION (turns toward + speeds up to destroy)
    - Pair 3 (Organic): Inhibitory Uncrossed -> LOVES (turns toward + slows/rests)
    - Pair 4 (Oxygen): Inhibitory Crossed -> EXPLORES (turns away + slows, orbits)
    """
    
    EXCITATORY_SCALE = 0.08
    INHIBITORY_SCALE = 0.12
    
    def __init__(self, x: float, y: float, heading: float = 0):
        super().__init__(x, y, heading=heading)
    
    def update(self, sources: List[Source]) -> None:
        self.left_motor = self.base_speed
        self.right_motor = self.base_speed
        
        # Sensor pair configurations: (SourceType, connection_type, crossing)
        configs = [
            (SourceType.TEMPERATURE, 'excitatory', 'uncrossed'),  # FEAR
            (SourceType.LIGHT, 'excitatory', 'crossed'),          # AGGRESSION
            (SourceType.ORGANIC, 'inhibitory', 'uncrossed'),      # LOVE
            (SourceType.OXYGEN, 'inhibitory', 'crossed'),         # EXPLORE
        ]
        
        for source_type, conn_type, crossing in configs:
            left_i = self._total_intensity(self.left_sensor_pos, sources, source_type)
            right_i = self._total_intensity(self.right_sensor_pos, sources, source_type)
            
            if conn_type == 'excitatory':
                scale = self.EXCITATORY_SCALE
                if crossing == 'uncrossed':
                    self.left_motor += left_i * scale
                    self.right_motor += right_i * scale
                else:  # crossed
                    self.left_motor += right_i * scale
                    self.right_motor += left_i * scale
            else:  # inhibitory
                scale = self.INHIBITORY_SCALE
                if crossing == 'uncrossed':
                    self.left_motor -= left_i * scale
                    self.right_motor -= right_i * scale
                else:  # crossed
                    self.left_motor -= right_i * scale
                    self.right_motor -= left_i * scale
        
        self._apply_motion()
    
    def draw(self, surface: pygame.Surface) -> None:
        self._draw_body(surface, (140, 70, 160), "3c: KNOWLEDGE")  # Purple
        self._draw_motor_bars(surface)


# -----------------------------------------------------------------------------
# Simulation State
# -----------------------------------------------------------------------------

class Simulation:
    """Manages the simulation state and rendering."""
    
    # Source placement modes for each vehicle zone
    SOURCE_MODES = {
        'left': SourceType.GENERIC,    # For 3a
        'center': SourceType.GENERIC,  # For 3b
        'right': None,                 # For 3c (uses number keys)
    }
    
    def __init__(self):
        self.reset()
        self.current_3c_type = SourceType.TEMPERATURE
    
    def reset(self) -> None:
        """Reset simulation to initial state."""
        # Three zones: left (3a), center (3b), right (3c)
        zone_width = WIDTH // 3
        
        self.vehicle_a = VehicleThreeA(zone_width // 2, HEIGHT // 2, heading=0)
        self.vehicle_b = VehicleThreeB(zone_width + zone_width // 2, HEIGHT // 2, heading=0)
        self.vehicle_c = VehicleThreeC(2 * zone_width + zone_width // 2, HEIGHT // 2, heading=0)
        
        self.sources: List[Source] = []
    
    def get_zone(self, x: int) -> str:
        """Determine which zone a x-coordinate is in."""
        zone_width = WIDTH // 3
        if x < zone_width:
            return 'left'
        elif x < 2 * zone_width:
            return 'center'
        else:
            return 'right'
    
    def add_source(self, x: int, y: int) -> None:
        """Add a source at the given position based on zone."""
        zone = self.get_zone(x)
        
        if zone == 'right':
            # 3c zone uses selected source type
            source_type = self.current_3c_type
        else:
            # 3a and 3b zones use GENERIC
            source_type = SourceType.GENERIC
        
        self.sources.append(Source(x, y, source_type))
    
    def update(self) -> None:
        """Update all vehicles."""
        zone_width = WIDTH // 3
        
        # Filter sources by zone for each vehicle
        sources_left = [s for s in self.sources if s.x < zone_width]
        sources_center = [s for s in self.sources if zone_width <= s.x < 2 * zone_width]
        sources_right = [s for s in self.sources if s.x >= 2 * zone_width]
        
        self.vehicle_a.update(sources_left)
        self.vehicle_b.update(sources_center)
        self.vehicle_c.update(sources_right)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all simulation elements."""
        zone_width = WIDTH // 3
        
        # Draw zone dividers
        pygame.draw.line(surface, (180, 180, 180), 
                        (zone_width, 0), (zone_width, HEIGHT), 2)
        pygame.draw.line(surface, (180, 180, 180), 
                        (2 * zone_width, 0), (2 * zone_width, HEIGHT), 2)
        
        # Draw zone headers
        headers = [
            ("ZONE 3a: LOVE", 10),
            ("ZONE 3b: EXPLORER", zone_width + 10),
            ("ZONE 3c: KNOWLEDGE", 2 * zone_width + 10),
        ]
        for text, x in headers:
            label = font_bold.render(text, True, (60, 60, 60))
            surface.blit(label, (x, 10))
        
        # Draw sources
        for source in self.sources:
            source.draw(surface)
        
        # Draw vehicles
        self.vehicle_a.draw(surface)
        self.vehicle_b.draw(surface)
        self.vehicle_c.draw(surface)
        
        # Draw instructions
        self._draw_instructions(surface)
    
    def _draw_instructions(self, surface: pygame.Surface) -> None:
        """Draw instruction panel."""
        instructions = [
            "Vehicle 3 Variants - Inhibitory Connections",
            "",
            "3a (left): Inhibitory Uncrossed - LOVES source, faces it",
            "3b (center): Inhibitory Crossed - EXPLORES, faces away",
            "3c (right): Multi-sensorial with VALUES",
            "",
            "For 3c zone, press 1-4 to select source type:",
            f"  1=Temp (avoids)  2=Light (attacks)  3=Organic (loves)  4=Oxygen (explores)",
            "",
            "Click to add sources | R = Reset all",
        ]
        
        y = HEIGHT - len(instructions) * 16 - 10
        for line in instructions:
            text = font.render(line, True, (50, 50, 50))
            surface.blit(text, (10, y))
            y += 16
        
        # Current 3c source type indicator
        type_colors = {
            SourceType.TEMPERATURE: (255, 100, 50),
            SourceType.LIGHT: (255, 230, 80),
            SourceType.ORGANIC: (80, 180, 80),
            SourceType.OXYGEN: (100, 160, 255),
        }
        color = type_colors.get(self.current_3c_type, (150, 150, 150))
        indicator = font_bold.render(f"3c Source: {self.current_3c_type.value}", 
                                     True, color)
        surface.blit(indicator, (WIDTH - 200, HEIGHT - 30))


# -----------------------------------------------------------------------------
# Main Loop
# -----------------------------------------------------------------------------

def main():
    sim = Simulation()
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    sim.reset()
                elif event.key == pygame.K_1:
                    sim.current_3c_type = SourceType.TEMPERATURE
                elif event.key == pygame.K_2:
                    sim.current_3c_type = SourceType.LIGHT
                elif event.key == pygame.K_3:
                    sim.current_3c_type = SourceType.ORGANIC
                elif event.key == pygame.K_4:
                    sim.current_3c_type = SourceType.OXYGEN
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                sim.add_source(event.pos[0], event.pos[1])
        
        # Update
        sim.update()
        
        # Render
        screen.fill((245, 245, 240))  # Off-white background
        sim.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()


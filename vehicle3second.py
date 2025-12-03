import pygame
import math
import random

pygame.init()

# -----------------------------------------------------------------------------
# CONSTANTS & CONFIG
# -----------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (Anti-AI / Earthy Palette)
COLOR_BG = (255, 255, 255)
COLOR_VEHICLE = (50, 50, 50)  # Charcoal
COLOR_TEXT = (20, 20, 20)

# Source Colors
COLOR_LIGHT = (255, 200, 0)    # Yellow
COLOR_TEMP = (200, 60, 0)      # Burnt Orange
COLOR_OXYGEN = (100, 200, 255) # Air Blue
COLOR_ORGANIC = (100, 150, 50) # Earth Green

# Sensor tuning (per-sense radius and falloff that reflect the prose in vehicle3.md)
SENSOR_SETTINGS = {
    "light":   {"range": 260, "curve": 1.0},  # light bulbs felt far away so the vehicle can charge at them
    "temp":    {"range": 220, "curve": 1.0},  # heat sensed a bit closer, enough to dodge before contact
    "oxygen":  {"range": 280, "curve": 1.8},  # oxygen gradients are gentle, encourage wide exploratory arcs
    "organic": {"range": 150, "curve": 2.2},  # organic scent only strong when near, so it can truly settle
}

# Motor influence weights (speed delta contributed by a fully saturated sensor)
WEIGHTS = {
    "temp": 2.4,      # uncrossed excitatory (runs away)
    "light": 3.1,     # crossed excitatory (charges to destroy bulbs)
    "oxygen": 1.4,    # crossed inhibitory (orbits / drifts away when scarce)
    "organic": 2.6,   # uncrossed inhibitory (slows down to rest near food)
}

# -----------------------------------------------------------------------------
# CLASSES
# -----------------------------------------------------------------------------

class Source:
    def __init__(self, x, y, type_name):
        self.x = x
        self.y = y
        self.type = type_name  # 'light', 'temp', 'oxygen', 'organic'
        self.radius = 15
        
    def get_color(self):
        if self.type == 'light': return COLOR_LIGHT
        if self.type == 'temp': return COLOR_TEMP
        if self.type == 'oxygen': return COLOR_OXYGEN
        if self.type == 'organic': return COLOR_ORGANIC
        return (0, 0, 0)

    def draw(self, surface):
        # Draw a faint "range" circle to show where sensors kick in
        settings = SENSOR_SETTINGS[self.type]
        pygame.draw.circle(surface, (240, 240, 240), (int(self.x), int(self.y)), int(settings["range"]), 1)
        pygame.draw.circle(surface, self.get_color(), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius, 2)

class VehicleThreeC:
    """
    Vehicle 3c: The Multisensorial Vehicle.
    Refined for visible behaviors: Rest, Attack, Flee, Explore.
    
    Sensors & Connections:
    1. Temperature -> Uncrossed Excitatory (2a behavior: Coward/Turns away)
    2. Light       -> Crossed Excitatory   (2b behavior: Aggressive/Turns toward)
    3. Oxygen      -> Crossed Inhibitory   (3b behavior: Explorer/Likes but orbits)
    4. Organic     -> Uncrossed Inhibitory (3a behavior: Lover/Stays close)
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.heading = 0 # Radians
        
        # Configuration
        self.sensor_dist = self.radius * 1.7
        self.sensor_angle = 0.85  # radians (~49 deg) to separate stimuli clearly across sensors
        
        # Tuned Physics
        self.base_speed = 1.4
        self.max_speed = 6.0
        self.min_speed = 0.05

    def get_sensor_pos(self, angle_offset):
        # Calculate sensor position in world space
        angle = self.heading + angle_offset
        sx = self.x + math.cos(angle) * self.sensor_dist
        sy = self.y + math.sin(angle) * self.sensor_dist
        return sx, sy

    def _sensor_strengths(self, sensor_pos, sources, target_type):
        """Aggregate normalized (0-1) stimulus strength for a single sensor."""
        sx, sy = sensor_pos
        config = SENSOR_SETTINGS[target_type]
        max_range = config["range"]
        curve = config["curve"]
        total = 0.0

        for src in sources:
            if src.type != target_type:
                continue
            dx = src.x - sx
            dy = src.y - sy
            dist = math.hypot(dx, dy)
            if dist >= max_range or dist == 0:
                continue
            strength = (max_range - dist) / max_range
            total += strength ** curve
        # cap to 1.0 so weights represent actual speed delta
        return min(total, 1.0)

    def update(self, sources):
        # Sensor Positions
        left_sensor = self.get_sensor_pos(self.sensor_angle)   # physically on vehicle's left
        right_sensor = self.get_sensor_pos(-self.sensor_angle) # physically on vehicle's right

        temp_l = self._sensor_strengths(left_sensor, sources, 'temp')
        temp_r = self._sensor_strengths(right_sensor, sources, 'temp')
        light_l = self._sensor_strengths(left_sensor, sources, 'light')
        light_r = self._sensor_strengths(right_sensor, sources, 'light')
        oxy_l = self._sensor_strengths(left_sensor, sources, 'oxygen')
        oxy_r = self._sensor_strengths(right_sensor, sources, 'oxygen')
        org_l = self._sensor_strengths(left_sensor, sources, 'organic')
        org_r = self._sensor_strengths(right_sensor, sources, 'organic')

        motor_l = self.base_speed
        motor_r = self.base_speed

        # Temperature (uncrossed excitatory)
        motor_l += temp_l * WEIGHTS["temp"]
        motor_r += temp_r * WEIGHTS["temp"]

        # Light (crossed excitatory)
        motor_l += light_r * WEIGHTS["light"]
        motor_r += light_l * WEIGHTS["light"]

        # Oxygen (crossed inhibitory)
        motor_l -= oxy_r * WEIGHTS["oxygen"]
        motor_r -= oxy_l * WEIGHTS["oxygen"]

        # Organic (uncrossed inhibitory)
        motor_l -= org_l * WEIGHTS["organic"]
        motor_r -= org_r * WEIGHTS["organic"]

        motor_l = max(self.min_speed, min(motor_l, self.max_speed))
        motor_r = max(self.min_speed, min(motor_r, self.max_speed))

        # Physics
        v_forward = (motor_l + motor_r) / 2
        
        # Turning Logic Fixed:
        # If Left Motor > Right Motor:
        #   Left side pushes harder -> Vehicle turns Clockwise (Right)
        #   Pygame Angle increases (+) -> Correct
        v_turn = (motor_l - motor_r) / (self.radius * 2.0) 
        
        self.heading += v_turn
        self.x += math.cos(self.heading) * v_forward
        self.y += math.sin(self.heading) * v_forward
        
        # Screen Wrap
        self.x %= WIDTH
        self.y %= HEIGHT

    def draw(self, surface):
        # Body
        pygame.draw.circle(surface, COLOR_VEHICLE, (int(self.x), int(self.y)), self.radius)
        # Rim
        pygame.draw.circle(surface, (0,0,0), (int(self.x), int(self.y)), self.radius, 2)
        
        # Sensors (Eyes)
        lx, ly = self.get_sensor_pos(self.sensor_angle)
        rx, ry = self.get_sensor_pos(-self.sensor_angle)
        pygame.draw.circle(surface, (200, 200, 200), (int(lx), int(ly)), 5)
        pygame.draw.circle(surface, (200, 200, 200), (int(rx), int(ry)), 5)
        
        # Direction
        ex = self.x + math.cos(self.heading) * (self.radius + 10)
        ey = self.y + math.sin(self.heading) * (self.radius + 10)
        pygame.draw.line(surface, (0,0,0), (self.x, self.y), (ex, ey), 2)
        
        # Label
        font = pygame.font.SysFont("consolas", 12)
        label = font.render("3c", True, (255, 255, 255))
        surface.blit(label, (self.x - 6, self.y - 6))

# -----------------------------------------------------------------------------
# MAIN SIMULATION
# -----------------------------------------------------------------------------

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Vehicle 3c - The Multisensorial")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 16)
    
    sources = []
    vehicle = VehicleThreeC(WIDTH//2, HEIGHT//2)
    
    current_source_type = 'light'
    
    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Mouse Click adds source
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                sources.append(Source(mx, my, current_source_type))
                
            # Keyboard changes source type
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: current_source_type = 'light'
                if event.key == pygame.K_2: current_source_type = 'temp'
                if event.key == pygame.K_3: current_source_type = 'oxygen'
                if event.key == pygame.K_4: current_source_type = 'organic'
                if event.key == pygame.K_r: sources = [] # Reset
                if event.key == pygame.K_SPACE: # Reset Vehicle
                    vehicle.x, vehicle.y = WIDTH//2, HEIGHT//2
                    vehicle.heading = 0

        # Update
        vehicle.update(sources)
        
        # Draw
        screen.fill(COLOR_BG)
        
        # Instructions
        info = [
            f"Current Tool: {current_source_type.upper()}",
            "1: Light (Aggressive/Attract)", 
            "2: Heat (Fear/Repel)", 
            "3: Oxygen (Explorer/Orbit)", 
            "4: Organic (Love/Stay)",
            "Click to Add Source | R: Clear All"
        ]
        
        for i, text in enumerate(info):
            col = COLOR_TEXT
            if "Tool" in text:
                if current_source_type == 'light': col = COLOR_LIGHT
                elif current_source_type == 'temp': col = COLOR_TEMP
                elif current_source_type == 'oxygen': col = COLOR_OXYGEN
                elif current_source_type == 'organic': col = COLOR_ORGANIC
                # Darken color for text readability on white
                col = tuple(max(0, c - 50) for c in col)
                
            lbl = font.render(text, True, col)
            screen.blit(lbl, (10, 10 + i * 20))

        for s in sources:
            s.draw(screen)
            
        vehicle.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()

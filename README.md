# Braitenberg Vehicles 3 & 4

Interactive simulations of Braitenberg's Vehicles 3 and 4, exploring emergent behavior through simple sensor-motor connections.

## Overview

This project implements Valentino Braitenberg's thought experiments on synthetic psychology, demonstrating how complex behaviors emerge from simple connections between sensors and motors.

## Files

### Finalized Implementations

- **`vehicle303.py`** - Vehicle 3 (Finalized)
  - **Vehicle 3a**: "Love" - Inhibitory uncrossed connections, comes to rest facing the source
  - **Vehicle 3b**: "Explorer" - Inhibitory crossed connections, explores but returns to sources
  - **Vehicle 3c**: "Multi-sensorial" - Four sensor pairs (Temperature, Light, Oxygen, Organic) with mixed excitatory/inhibitory and crossed/uncrossed connections

- **`vehicle4.py`** - Vehicle 4 (Finalized)
  - **Vehicle 4a**: Non-monotonic (Gaussian) response curves - motor speed peaks at optimal intensity, creating orbiting/figure-8 behaviors
  - **Vehicle 4b**: Threshold-based connections with abrupt changes - creates "decision-like" behavior with deliberation before action

### Additional Files

- **`vehicle4_comparison.py`** - Side-by-side comparison of Gaussian (non-linear) vs Linear (monotonic) response functions
- **`vehicle3.md`** - Original description of Vehicle 3 from Braitenberg
- **`vehicle4.md`** - Original description of Vehicle 4 from Braitenberg

## Vehicle 3: Love, Explorer, and Values

### Key Concepts

**Vehicle 3a (Love)**
- Inhibitory uncrossed connections
- Slows down near sources
- Comes to rest facing the source
- "Loves" the source in a permanent way

**Vehicle 3b (Explorer)**
- Inhibitory crossed connections
- Slows down near sources but faces away
- Explores, seeking stronger sources
- More dynamic behavior

**Vehicle 3c (Multi-sensorial)**
- Four sensor pairs: Temperature, Light, Oxygen, Organic matter
- Mixed connection types:
  - Temperature: Excitatory uncrossed (turns away from heat)
  - Light: Excitatory crossed (approaches and destroys light bulbs)
  - Oxygen: Inhibitory crossed (prefers well-oxygenated areas)
  - Organic: Inhibitory uncrossed (seeks organic matter)
- Demonstrates "values" and "knowledge" through behavior

### Running Vehicle 3

```bash
python vehicle303.py
```

**Controls:**
- `1-4`: Select source type (Temperature, Light, Oxygen, Organic)
- `A`: Switch to Vehicle 3a (Love)
- `B`: Switch to Vehicle 3b (Explorer)
- `C`: Switch to Vehicle 3c (Multi-sensorial)
- `Click`: Add source at mouse position
- `R`: Reset board

## Vehicle 4: Values and Special Tastes

### Key Concepts

**Non-Monotonic Response (Vehicle 4a)**
- Motor speed has a **maximum** at optimal intensity
- Below optimal: motor speeds up (approaching behavior)
- Above optimal: motor slows down (avoiding behavior)
- Creates orbiting, figure-8, and complex trajectories
- Uses **Gaussian bell curve** response function

**Threshold Response (Vehicle 4b)**
- Motor doesn't activate until stimulus reaches threshold
- Abrupt changes in behavior
- Creates "decision-like" deliberation
- Appears to "ponder" before acting

### The Critical Difference: Non-Linear vs Linear

**Vehicle 4a (Gaussian/Non-linear):**
```
Response = exp(-((intensity - optimal)²) / (2 × width²))
```
- Has a **peak** at optimal intensity
- Symmetric falloff on both sides
- Creates stable orbiting behavior

**Linear/Monotonic (Vehicle 3 style):**
```
Response = intensity × slope
```
- No peak - continuously increases
- "The more, the more" behavior
- Rushes toward sources, may crash

### Running Vehicle 4

```bash
python vehicle4.py
```

**Controls:**
- `1-4`: Select source type (Light, Sound, Smell, Heat)
- `A`: Switch to Vehicle 4a (Gaussian response)
- `B`: Switch to Vehicle 4b (Threshold response)
- `Click`: Add source at mouse position
- `R`: Reset board

### Running Comparison

```bash
python vehicle4_comparison.py
```

Shows side-by-side comparison of Gaussian vs Linear response functions with real-time graphs.

## Technical Details

### Dependencies

- Python 3.9+
- pygame 2.6.1+

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install pygame
```

### Physics Model

- **Intensity Calculation**: Inverse square law `I = k / d²`
- **Motor Speed**: Base speed + sensor response × boost factor
- **Turning Rate**: Differential drive `ω = (v_left - v_right) / wheelbase`
- **Position Update**: Euler integration with heading-based velocity

### Response Functions

**Gaussian (Vehicle 4a):**
- Optimal intensity: 120-200 (configurable per source type)
- Curve width: 60-120 (controls sharpness of peak)
- Creates non-monotonic "preference" for optimal distance

**Threshold (Vehicle 4b):**
- Threshold: 40-80 (minimum intensity to activate)
- Minimum activation: 1.0-1.8 (jump value at threshold)
- Slope: 0.010-0.020 (linear increase after threshold)

## Behavioral Observations

### Vehicle 3 Behaviors

- **3a**: Stable, "loving" behavior - stays near sources
- **3b**: Dynamic exploration - seeks better sources
- **3c**: Complex multi-objective behavior - appears to have "values"

### Vehicle 4 Behaviors

- **4a**: 
  - Orbits single sources at optimal distance
  - Creates figure-8 patterns between two sources
  - Alternates between sources based on intensity
  - "Instinctual" complex trajectories

- **4b**:
  - Deliberates before moving (threshold delay)
  - Abrupt action once threshold crossed
  - Appears to "make decisions"
  - More "spontaneous" than lower vehicles

## References

Based on Valentino Braitenberg's "Vehicles: Experiments in Synthetic Psychology" (1984)

- **Chapter 3**: "Love" - Inhibitory connections
- **Chapter 4**: "Values and Special Tastes" - Non-monotonic connections

## Notes

- Vehicle 3 and 4 demonstrate how simple rules create complex, lifelike behaviors
- The distinction between excitatory/inhibitory and crossed/uncrossed connections creates rich behavioral variety
- Non-monotonic responses (Vehicle 4) introduce "optimal" states, creating more sophisticated navigation
- Threshold responses (Vehicle 4b) create the appearance of "decision-making" and "free will"


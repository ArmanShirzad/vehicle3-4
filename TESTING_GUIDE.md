# Testing Guide for Vehicle 3 & 4 Simulations

## Quick Start: How to Run and Test

1. **Install dependencies**: Ensure `pygame` is installed (`pip install pygame` or `pip3 install pygame`)
2. **Run vehicle303.py**: Execute `python3 vehicle303.py` to launch Vehicle 3c simulation (multi-sensorial with inhibitory/excitatory connections)
3. **Run vehicle4.py**: Execute `python3 vehicle4.py` to launch Vehicle 4a/4b simulation (non-monotonic and threshold connections)
4. **Test interactions**: Click to add sources, use number keys (1-4) to switch source types, press 'R' to reset, and press 'A'/'B' in vehicle4.py to toggle vehicle types
5. **Verify behaviors**: Observe vehicle trajectories—Vehicle 3c should show complex multi-sensorial behavior (avoiding temperature, attacking light, loving organic matter, exploring oxygen), while Vehicle 4a should orbit sources at optimal distance and Vehicle 4b should show threshold-based "deliberation" before acting

---

## TA Questions: vehicle303.py (Vehicle 3c)

### Based on vehicle3.md - Inhibitory Connections & Multi-sensorial Behavior

**Q1: Explain the difference between excitatory and inhibitory connections in Vehicle 3c. How does each sensor pair contribute to the vehicle's behavior?**

**Expected Answer**: Excitatory connections increase motor speed when sensors detect stimuli (used for Temperature—avoidance/fear—and Light—aggression). Inhibitory connections decrease motor speed when sensors detect stimuli (used for Organic matter—love/attraction—and Oxygen—exploration). The vehicle combines all four sensor pairs: Temperature (excitatory uncrossed) makes it turn away and speed up from hot places; Light (excitatory crossed) makes it turn toward and attack light sources; Organic (inhibitory uncrossed) makes it turn toward and slow down near organic matter, eventually resting; Oxygen (inhibitory crossed) makes it turn away but slow down, creating orbital exploration behavior.

**Q2: According to the text, Vehicle 3a "LOVES" the source and comes to rest facing it, while Vehicle 3b is an "EXPLORER" that faces away. How does Vehicle 3c implement these behaviors simultaneously?**

**Expected Answer**: Vehicle 3c uses multiple sensor pairs with different connection types. The Organic matter sensor pair uses inhibitory uncrossed connections (like 3a), causing the vehicle to turn toward and rest near organic sources. The Oxygen sensor pair uses inhibitory crossed connections (like 3b), causing the vehicle to turn away from oxygen sources while still being attracted to them, creating exploration behavior. The vehicle can exhibit both "love" and "exploration" behaviors simultaneously because each sensor pair responds independently to its specific source type.

**Q3: The text states that Vehicle 3c "has a system of VALUES, and, come to think of it, KNOWLEDGE." How does the code implement this apparent knowledge, and why does the text caution against calling it true knowledge?**

**Expected Answer**: The code implements apparent knowledge through the specific sensor-motor connections: the vehicle avoids temperature and attacks light bulbs (as if it knows light bulbs heat the environment), and it prefers oxygen and organic matter (as if it knows these are needed for energy). However, this is not true knowledge because there is no information flow or learning mechanism—it's just hardcoded sensor-motor connections. The text cautions that true knowledge requires information transmission and will be discussed in later vehicles (6 and 7).

**Q4: What happens when the vehicle approaches a source with inhibitory connections? Why does it "come to rest in the immediate vicinity of the source"?**

**Expected Answer**: With inhibitory connections, as the vehicle approaches a source, the sensor intensity increases, which decreases motor speed. When the vehicle gets very close, the intensity becomes very high (due to inverse square law), causing the motors to slow down significantly. The inhibitory scale (0.150) is strong enough that at close range, the motor speeds can approach zero, allowing the vehicle to come to rest. The code ensures motors don't go negative (max(0.0, motor)), allowing complete rest at zero speed.

**Q5: How does the inverse square law intensity calculation affect the vehicle's ability to rest near sources? What would happen if you used a linear or constant intensity function instead?**

**Expected Answer**: The inverse square law (`intensity = 50000.0 / (distance * distance)`) means intensity increases dramatically as distance decreases. At distance 10, intensity is ~500; at distance 1, intensity is ~50,000. This strong gradient allows inhibitory connections to effectively slow the vehicle to rest when very close. With linear intensity, the gradient would be weaker, and the vehicle might not slow down enough to rest. With constant intensity, there would be no distance-based response, and the vehicle couldn't exhibit proximity-based behaviors like resting or orbiting.

---

## TA Questions: vehicle4.py (Vehicle 4a & 4b)

### Based on vehicle4.md - Non-monotonic Connections & Threshold Behavior

**Q1: Explain the difference between monotonic and non-monotonic connections. How does Vehicle 4a's bell curve response create orbiting behavior?**

**Expected Answer**: Monotonic connections are "the more, the more" or "the more, the less"—motor speed always increases or always decreases with sensor intensity. Non-monotonic connections have a peak: motor speed increases up to an optimal intensity, then decreases beyond that point. Vehicle 4a uses a Gaussian bell curve (`_bell_curve_response`) centered at an optimal intensity. When the vehicle is far from a source, intensity is below optimal, so it speeds up and approaches. When too close, intensity exceeds optimal, so it slows down and turns away. This creates a stable orbit at the optimal distance where corrections toward and away from the source balance out.

**Q2: The text describes Vehicle 4a as having "INSTINCTS" with "complicated trajectories" including figure-eights and orbits. How does the code enable this variety of behaviors?**

**Expected Answer**: The code enables varied behaviors through different optimal intensities and curve widths for each source type (Light: 150.0, Sound: 200.0, Smell: 100.0, Heat: 80.0), combined with different connection types (crossed/uncrossed). When multiple sources are present, the vehicle responds to all of them simultaneously, creating complex combined trajectories. The vehicle might approach one source until it exceeds optimal intensity, then turn toward another, creating figure-eight patterns or alternating visits between sources.

**Q3: What is the mathematical function used for the bell curve response in Vehicle 4a, and how do the `optimal_intensity` and `curve_width` parameters affect the vehicle's behavior?**

**Expected Answer**: The bell curve uses a Gaussian function: `exp(-((intensity - optimal)² / (2 * width²)))`. This returns a value between 0 and 1, peaking at 1 when intensity equals optimal. The `optimal_intensity` determines the distance at which the vehicle prefers to orbit (higher values mean the vehicle prefers to be farther from the source). The `curve_width` controls how sharply the response drops off (smaller width = sharper peak = more precise orbiting distance, larger width = more gradual response = less precise but more stable behavior).

**Q4: Vehicle 4b implements threshold-based connections. Explain how the `_threshold_response` function creates "deliberation" behavior, and why the text says these vehicles "ponder over their DECISIONS."**

**Expected Answer**: The `_threshold_response` function returns 0.0 when intensity is below the threshold, meaning the motor receives no activation from that sensor. Only when intensity exceeds the threshold does the motor activate, jumping to a minimum activation value and then increasing linearly. This creates a delay: the vehicle must approach a source until the threshold is crossed before it responds. This delay appears as "deliberation" or "pondering"—the vehicle seems to wait and consider before acting, rather than responding immediately like monotonic vehicles.

**Q5: The text states that Vehicle 4b vehicles "act in a spontaneous way" and suggests this relates to "free will." How does the threshold mechanism create this appearance of spontaneity, and what is the philosophical implication?**

**Expected Answer**: The threshold creates abrupt, binary-like responses: below threshold, no action; above threshold, immediate activation. This creates the appearance of a "decision point" rather than gradual, passive attraction/repulsion. The vehicle seems to "choose" when to act based on crossing the threshold, appearing more autonomous than vehicles that simply follow gradients. The text suggests that the existence of decision-making (thresholds) might be a criterion for free will, though this is philosophical speculation—the behavior is still deterministic, just with discrete activation points rather than continuous responses.

**Q6: How would you modify Vehicle 4a to create a vehicle that likes weak stimuli but dislikes strong stimuli of the same type? How would this differ from Vehicle 3's inhibitory connections?**

**Expected Answer**: You could use a bell curve with a very low optimal intensity (e.g., 50.0) and a narrow curve width, combined with inhibitory connections (subtracting the bell curve response from motor speed instead of adding). This would make the vehicle slow down most at the optimal (weak) intensity and speed up when intensity is too high or too low. This differs from Vehicle 3's inhibitory connections because Vehicle 3's response is monotonic (always slows down as intensity increases), while this would be non-monotonic (slows down at weak intensity, speeds up at strong intensity), creating more complex "preference" behavior.

**Q7: In Vehicle 4b, what happens if you set the threshold very high and the minimum activation very low? How would this affect the vehicle's apparent "decision-making" behavior?**

**Expected Answer**: A very high threshold means the vehicle must get very close to a source before responding, creating a longer "deliberation" period. A very low minimum activation means that even after the threshold is crossed, the response is weak initially, creating a more gradual "decision" rather than an abrupt jump. This would make the vehicle appear more cautious and thoughtful, with a longer consideration phase followed by a gentle rather than sudden action. The slope parameter would then determine how quickly the response increases after the initial activation.


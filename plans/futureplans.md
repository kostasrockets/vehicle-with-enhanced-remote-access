## Velocity Matching
Thank you for this description Claude.

Each encoder counts ticks as the wheel spins. By checking how many ticks accumulate each loop cycle, you get a real velocity in ticks/sec. That measured velocity gets compared to your target velocity (whatever the ramp has ramped up to), and the difference — the error — tells you how far off you are.
If Motor A is running slow, its error is large, so the PID pushes more power to it. If it's running at exactly the right speed, the error is zero and the PID just holds steady. This happens dozens of times per second, constantly self-correcting.
The sync part adds one more ingredient: the difference between the two encoders. If Motor A is running at 480 ticks/sec and Motor B is at 520, even though both are "close enough" to the 500 target, they'll still cause the robot to drift. So you take that 40 tick/sec gap and add a small correction — slow B down slightly, speed A up slightly — until they match. It's essentially a third error signal on top of each motor's own speed error.
The result is that each motor is chasing two things at once: its own target speed, and its partner's speed. If either drifts, both signals push it back into line.

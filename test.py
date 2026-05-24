import pigpio
from time import sleep

GPIO_PIN = 18  # GPIO 18 = physical pin 12, a hardware PWM pin

# ESC pulse widths in microseconds (standard RC protocol)
NEUTRAL      = 1500  # us — true zero throttle
FULL_FORWARD = 2000  # us
FULL_REVERSE = 1000  # us

NEUTRAL_HOLD = 1.5   # seconds to dwell at neutral
STEP_DELAY   = 0.05  # seconds between steps

pi = pigpio.pi()

if not pi.connected:
    raise RuntimeError("pigpio daemon not running. Start it with: sudo pigpiod")

def set_pulsewidth(us):
    pi.set_servo_pulsewidth(GPIO_PIN, us)

def set_neutral(hold=NEUTRAL_HOLD):
    set_pulsewidth(NEUTRAL)
    sleep(hold)

# Arm ESC
print("Arming...")
set_neutral(hold=2)
print("Armed!")

try:
    while True:
        # Neutral -> Full Forward
        print("Ramping forward...")
        for us in range(NEUTRAL, FULL_FORWARD + 1, 5):
            set_pulsewidth(us)
            sleep(STEP_DELAY)

        sleep(0.5)

        # Full Forward -> Neutral
        print("Braking to neutral...")
        for us in range(FULL_FORWARD, NEUTRAL - 1, -5):
            set_pulsewidth(us)
            sleep(STEP_DELAY)

        print("Holding neutral...")
        set_neutral(hold=NEUTRAL_HOLD)

        # Neutral -> Full Reverse
        print("Ramping to reverse...")
        for us in range(NEUTRAL, FULL_REVERSE - 1, -5):
            set_pulsewidth(us)
            sleep(STEP_DELAY)

        sleep(0.5)

        # Full Reverse -> Neutral
        print("Braking to neutral...")
        for us in range(FULL_REVERSE, NEUTRAL + 1, 5):
            set_pulsewidth(us)
            sleep(STEP_DELAY)

        print("Holding neutral...")
        set_neutral(hold=NEUTRAL_HOLD)

except KeyboardInterrupt:
    print("Stopping...")
    set_pulsewidth(0)  # Turn off PWM signal entirely
    pi.stop()
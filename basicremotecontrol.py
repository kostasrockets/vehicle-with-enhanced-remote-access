import paho.mqtt.client as mqtt
import threading
import pigpio
from time import sleep

MOTOR_1_GPIO = 18   # BCM GPIO 18, physical pin 12
MOTOR_2_GPIO = 12   # BCM GPIO 12, physical pin 32 — confirm this for your wiring

NEUTRAL      = 1500
FULL_FORWARD = 1750
FULL_REVERSE = 1250
NEUTRAL_HOLD = 0.5
STEP_DELAY   = 0.05

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("pigpio daemon not running. Start it with: sudo pigpiod")

stop_event   = threading.Event()   # was missing
motor_thread = None                 # was missing

def invert(us):
    """Flip a pulse width around neutral — 2000 becomes 1000, 1500 stays 1500, etc."""
    return NEUTRAL - (us - NEUTRAL)

def set_pulsewidth(us, motor_id):
    if motor_id == 1:
        pi.set_servo_pulsewidth(MOTOR_1_GPIO, us)
    elif motor_id == 2:
        pi.set_servo_pulsewidth(MOTOR_2_GPIO, invert(us))  

def set_neutral(hold=NEUTRAL_HOLD):
    set_pulsewidth(NEUTRAL, 1)
    set_pulsewidth(NEUTRAL, 2)
    sleep(hold)

def stop_motor():
    global motor_thread
    stop_event.set()
    if motor_thread and motor_thread.is_alive():
        motor_thread.join()
    stop_event.clear()

def ramp_forward():
    print("Ramping forward...")
    for us in range(NEUTRAL, FULL_FORWARD + 1, 5):
        if stop_event.is_set():
            break
        set_pulsewidth(us, 1)
        set_pulsewidth(us, 2)
        sleep(STEP_DELAY)

def ramp_reverse():
    print("Ramping reverse...")
    for us in range(NEUTRAL, FULL_REVERSE - 1, -5):
        if stop_event.is_set():
            break
        set_pulsewidth(us, 1)
        set_pulsewidth(us, 2)
        sleep(STEP_DELAY)

def ramp_left():
    print("Ramping left...")
    for us in range(NEUTRAL, FULL_REVERSE - 1, -5):
        if stop_event.is_set():
            break
        set_pulsewidth(us, 2)
        sleep(STEP_DELAY)

def ramp_right():
    print("Ramping left...")
    for us in range(NEUTRAL, FULL_REVERSE - 1, -5):
        if stop_event.is_set():
            break
        set_pulsewidth(us, 1)
        sleep(STEP_DELAY)


# Arm ESC
print("Arming...")
set_neutral(hold=2)
print("Armed!")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("vera/#")

def on_message(client, userdata, msg):
    global motor_thread
    command = msg.payload.decode().strip()
    print(f"Received: {msg.topic} -> {command}")

    stop_motor()  # interrupt anything running

    if command == "forward":
        motor_thread = threading.Thread(target=ramp_forward, daemon=True)
        motor_thread.start()
    elif command == "backwards":
        motor_thread = threading.Thread(target=ramp_reverse, daemon=True)
        motor_thread.start()
    elif command == "left":
        motor_thread = threading.Thread(target=ramp_left, daemon=True)
        motor_thread.start()
    elif command == "right":
        motor_thread = threading.Thread(target=ramp_right, daemon=True)
        motor_thread.start()
    elif command in ("stop"):
        print("Stopped.")
        set_neutral()
    else:
        print(f"Unknown command: {command}")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("141.148.156.227", 1883, 60)

try:
    mqttc.loop_forever()
except KeyboardInterrupt:
    print("Shutting down...")
finally:
    stop_motor()
    set_pulsewidth(0, 1)
    set_pulsewidth(0, 2)
    pi.stop()
    mqttc.disconnect()
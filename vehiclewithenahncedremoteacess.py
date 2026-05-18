'''
Control the Brightness of LED using PWM on Raspberry Pi
http://www.electronicwings.com
'''

from time import sleep

try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    # Provide a lightweight mock for non-Raspberry Pi environments
    class _MockPWM:
        def __init__(self, pin, freq):
            self.pin = pin
            self.freq = freq
            self.duty = 0
        def start(self, duty):
            self.duty = duty
        def ChangeDutyCycle(self, duty):
            self.duty = duty
        def stop(self):
            pass

    class GPIO:
        BOARD = 'BOARD'
        OUT = 'OUT'
        _pwms = {}

        @staticmethod
        def setwarnings(flag):
            pass

        @staticmethod
        def setmode(mode):
            pass

        @staticmethod
        def setup(pin, mode):
            pass

        @staticmethod
        def PWM(pin, freq):
            pwm = _MockPWM(pin, freq)
            GPIO._pwms[pin] = pwm
            return pwm

        @staticmethod
        def cleanup():
            GPIO._pwms.clear()


ledpin = 12				# PWM pin connected to LED
GPIO.setwarnings(False)			#disable warnings
GPIO.setmode(GPIO.BOARD)		#set pin numbering system
GPIO.setup(ledpin,GPIO.OUT)
pi_pwm = GPIO.PWM(ledpin,1000)		#create PWM instance with frequency
pi_pwm.start(0)				#start PWM of required Duty Cycle 
while True:
    for duty in range(0,101,1):
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
        sleep(0.01)
    sleep(0.5)
    
    for duty in range(100,-1,-1):
        pi_pwm.ChangeDutyCycle(duty)
        sleep(0.01)
    sleep(0.5)
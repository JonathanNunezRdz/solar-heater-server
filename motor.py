import RPi.GPIO as GPIO
from time import sleep
"""
    TO-DO: 
        [] This script controls the motor, add to index_mk2.py
"""

in1 = 24
in2 = 23
en = 25
temp1 = 1

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(in1, GPIO.OUT)
# GPIO.setup(in2, GPIO.OUT)
# GPIO.setup(en, GPIO.OUT)

GPIO.output(in1, GPIO.HIGH)
GPIO.output(in2, GPIO.LOW)

motor = GPIO.PWM(en, 1000)
motor_duty_cycle = 100

def forward():
    motor.stop()
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    print('forward')

def backward():
    motor.stop()
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.HIGH)
    print('backwards')

while(True):
    print("\n")
    print("The default speed & direction of motor is LOW & Forward.....")
    print("r-run s-stop f-forward b-backward l-low m-medium h-high e-exit")
    print("\n")
    x=input()
    
    if x=='r':
        print("run")
        motor.start(motor_duty_cycle)
        print(motor_duty_cycle)
        x='z'


    elif x=='s':
        print("stop")
        motor.stop()
        x='z'

    elif x=='f':
        forward()
        x='z'

    elif x=='b':
        backward()
        x='z'

    elif x=='l':
        print("low")
        motor.stop()
        motor.ChangeDutyCycle(25)
        motor_duty_cycle = 25
        x='z'

    elif x=='m':
        print("medium")
        motor.stop()
        motor.ChangeDutyCycle(50)
        motor_duty_cycle = 50
        x='z'

    elif x=='h':
        print("high")
        motor.stop()
        motor.ChangeDutyCycle(75)
        motor_duty_cycle = 75
        x='z'

    elif x=='xh':
        print("high")
        motor.stop()
        motor.ChangeDutyCycle(100)
        motor_duty_cycle = 100
        x='z'
     
    
    elif x=='e':
        motor.stop()
        GPIO.cleanup()
        break
    
    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")

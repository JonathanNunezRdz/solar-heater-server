import RPi.GPIO as GPIO
from time import sleep
from gpio_functions import pin_on, pin_off
from index_mk2 import CHANNEL_MOTOR_IN_1, CHANNEL_MOTOR_IN_2, CHANNEL_MOTOR_ENABLE, MOTOR_DUTY_CYCLE

def setup_motor():
    GPIO.output(CHANNEL_MOTOR_IN_1, GPIO.HIGH)
    GPIO.output(CHANNEL_MOTOR_IN_2, GPIO.LOW)
    motor = GPIO.PWM(CHANNEL_MOTOR_ENABLE, 1000)
    return motor

def set_motor_up()->bool:
    # set input 1 to HIGH and input 2 to LOW
    pin_on(CHANNEL_MOTOR_IN_1)
    pin_off(CHANNEL_MOTOR_IN_2)
    print('changed direction to up')
    return True

def set_motor_down()->bool:
    # set input 1 to HIGH and input 2 to LOW
    pin_off(CHANNEL_MOTOR_IN_1)
    pin_on(CHANNEL_MOTOR_IN_2)
    print('changed direction to down')
    return True

def toggle_on_off(motor, duration:float)->bool:
    motor.start(MOTOR_DUTY_CYCLE) 
    sleep(duration)
    motor.stop()
    return True
import RPi.GPIO as GPIO
from time import sleep
from gpio_functions import pin_on, pin_off
from index_mk2 import CHANNEL_MOTOR_IN_1, CHANNEL_MOTOR_IN_2, CHANNEL_MOTOR_ENABLE

def setup_motor():
    motor = GPIO.PWM(CHANNEL_MOTOR_ENABLE, 1000)
    return motor

def set_motor_up()->bool:
    # set input 1 to HIGH and input 2 to LOW
    pin_on(CHANNEL_MOTOR_IN_1)
    pin_off(CHANNEL_MOTOR_IN_2)

    return True

def set_motor_down()->bool:
    # set input 1 to HIGH and input 2 to LOW
    pin_off(CHANNEL_MOTOR_IN_1)
    pin_on(CHANNEL_MOTOR_IN_2)

    return True

def toggle_on_off(motor, motor_duty_cycle:int ,duration:float, inverse:bool=False)->bool:
    if (inverse): pin_on(CHANNEL_MOTOR_ENABLE, 0)
    else: motor.start(motor_duty_cycle)
    sleep(duration)
    if (inverse): pin_off(CHANNEL_MOTOR_ENABLE, 1)
    else: motor.stop(motor_duty_cycle)

    return True
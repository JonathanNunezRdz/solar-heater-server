import RPi.GPIO as GPIO
import sys

def do_cleanup()->None:
    GPIO.cleanup()
    print('cleanup done - ready to exit')
    return None

def finalize(ctrl:bool)->None:
    if ctrl: print('pressed "ctrl + c"')
    do_cleanup()
    sys.exit(0)

def on_exit(sig, frame)->None:
    finalize(True)

def setup_gpio(channels:list)->None:
    GPIO.setmode(GPIO.BCM)
    for channel in channels:
        GPIO.setup(channel, GPIO.OUT)
    return None

def pin_on(pin:int, value:int=1)->None:
    GPIO.output(pin, value)
    print('pin {} on'.format(pin))
    return None

def pin_off(pin:int, value:int=0)->None:
    GPIO.output(pin, value)
    print('pin {} off'.format(pin))
    return None

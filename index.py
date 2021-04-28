#!/usr/bin/python

import RPi.GPIO as GPIO
import smbus
import math
from flask import Flask, jsonify, make_response, request
import sys
import signal
from time import sleep


app = Flask(__name__)

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for revision 2 boards
address = 0x68 # This is the address value read via the i2cdetect command

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a) + (b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def do_cleanup():
    GPIO.cleanup()
    print('cleanup done - ready to exit')
    return None

def finalize(ctrl:bool):
    if ctrl: print('pressed ctrl + c')
    
    do_cleanup()
    sys.exit()

def on_exit(sig, frame):
    finalize(True)

def gpio_setup(channels:list):
    GPIO.setmode(GPIO.BCM)
    for channel in channels:
        GPIO.setup(channel, GPIO.OUT, initial=1)
    return None

def pin_on(pin:int):
    GPIO.output(pin, 0)
    print('pin {} on'.format(pin))
    return None

def pin_off(pin:int):
    GPIO.output(pin, 1)
    print('pin {} off'.format(pin))
    return None

def set_motor_up():
    global channel_relay_master, channel_relay_negative, channel_relay_positive
    # turn off master relay
    pin_off(channel_relay_master)
    # set both positive and negative channels off
    pin_off(channel_relay_negative)
    pin_off(channel_relay_positive)

    return None

def set_motor_down():
    global channel_relay_master, channel_relay_negative, channel_relay_positive
    # turn off master relay
    pin_off(channel_relay_master)
    # set both positive and negative channels off
    pin_on(channel_relay_negative)
    pin_on(channel_relay_positive)

    return None

def toggle_on_off(pin:int, duration:float):
    pin_on(pin)
    # t = Timer(duration, pin_off, [pin])
    # t.start()
    sleep(duration)
    pin_off(pin)

    return None

def config_response(data):
    response = make_response(jsonify(data), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/')
def index():
    global channel_relay_positive, channel_relay_negative, channel_relay_master

    # Now wake the 6050 up as it starts in sleep mode
    bus.write_byte_data(address, power_mgmt_1, 0)

    # Setup GPIO to use channel 17, 27, 22 as OUT
    channel_relay_negative = 17
    channel_relay_positive = 27
    channel_relay_master = 22

    channel_list = [channel_relay_negative, channel_relay_positive, channel_relay_master]

    gpio_setup(channel_list)

    data = {
        'status': 1,
        'message': 'setup complete'
    }

    response = config_response(data)

    return response

@app.route('/mpu')
def mpu():
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)
    
    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0

    data = {
        'x_rotation' : get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled),
        'y_rotation' : get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
    }

    response = config_response(data)

    return response

@app.route('/toggle_motor')
def toggle_motor():
    global channel_relay_master
    duration = request.args.get('duration')
    toggle_on_off(channel_relay_master, float(duration))

    data = {
        'status': 1,
        'duration': duration
    }

    response = config_response(data)

    return response


@app.route('/pin_on')
def turn_pin_on():
    global channel_relay_master
    pin_on(channel_relay_master)

    data = {
        'status': 1,
    }

    response = make_response(jsonify(data), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/pin_off')
def turn_pin_off():
    global channel_relay_master
    pin_off(channel_relay_master)

    data = {
        'status': 0,
    }

    response = make_response(jsonify(data), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/current_direction')
def current_direction():
    return None

if __name__ == "__main__":
    print("running from main")
    signal.signal(signal.SIGINT, on_exit)
else:
    signal.signal(signal.SIGINT, on_exit)
    
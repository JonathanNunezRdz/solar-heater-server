#!/usr/bin/python

import RPi.GPIO as GPIO
import smbus
import math
from flask import Flask, jsonify, make_response, request
import sys
import signal
from time import sleep, time


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

def pin_on(pin:int, status:int=1):
    GPIO.output(pin, status)
    print('pin {} on'.format(pin))
    return None

def pin_off(pin:int, status:int=0):
    GPIO.output(pin, status)
    print('pin {} off'.format(pin))
    return None

def set_motor_up():
    global CHANNEL_MOTOR_IN_A, CHANNEL_MOTOR_ENABLE, CHANNEL_MOTOR_IN_B
    # set l294d enable to LOW 
    pin_off(CHANNEL_MOTOR_ENABLE)
    # set input A to HIGH and input B to LOW
    # pin_on(CHANNEL_MOTOR_IN_A)
    # pin_off(CHANNEL_MOTOR_IN_B)

    return None

def set_motor_down():
    global CHANNEL_MOTOR_IN_A, CHANNEL_MOTOR_ENABLE, CHANNEL_MOTOR_IN_B
    # set l294d enable to LOW 
    pin_off(CHANNEL_MOTOR_ENABLE)
    # set input A to LOW and input B to HIGH
    # pin_off(CHANNEL_MOTOR_IN_A)
    # pin_on(CHANNEL_MOTOR_IN_B)

    return None

def toggle_on_off(duration:float, inverse:bool=False):
    global CHANNEL_MOTOR_ENABLE
    if (inverse): pin_on(CHANNEL_MOTOR_ENABLE, 0)
    else: pin_on(CHANNEL_MOTOR_ENABLE)
    # t = Timer(duration, pin_off, [pin])
    # t.start()
    sleep(duration)
    if (inverse): pin_off(CHANNEL_MOTOR_ENABLE, 1)
    else: pin_off(CHANNEL_MOTOR_ENABLE)

    return None

def get_acceleration():
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)

    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0

    return {
        'x': round(accel_xout_scaled, 2),
        'y': round(accel_yout_scaled, 2), 
        'z': round(accel_zout_scaled, 2)
    }

def mpu_average():
    avg_xout = 0
    avg_yout = 0
    avg_zout = 0

    for i in range(10):
        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)
        
        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        avg_xout += accel_xout_scaled
        avg_yout += accel_yout_scaled
        avg_zout += accel_zout_scaled

    avg_xout = avg_xout / 10.0
    avg_yout = avg_yout / 10.0
    avg_zout = avg_zout / 10.0
    

    data = {
        'x_rotation' : get_x_rotation(avg_xout, avg_yout, avg_zout),
        'y_rotation' : get_y_rotation(avg_xout, avg_yout, avg_zout)
    }

    return data

def config_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'

    return response

def main():
    bus.write_byte_data(address, power_mgmt_1, 0)
    while(True):
        sleep(0.1)
        print(get_acceleration())

@app.route('/')
def index():
    global CHANNEL_MOTOR_ENABLE, current_direction, motor_status

    # Now wake the 6050 up as it starts in sleep mode
    bus.write_byte_data(address, power_mgmt_1, 0)

    # Setup GPIO to use channel 25 as OUT
    CHANNEL_MOTOR_ENABLE = 25

    channel_list = [CHANNEL_MOTOR_ENABLE]

    gpio_setup(channel_list)

    current_direction = 1
    motor_status = 0

    data = {
        'status': 1,
        'message': 'setup complete'
    }

    response = config_response(data)

    return response

@app.route('/mpu')
def mpu():
    avg_xout = 0
    avg_yout = 0
    avg_zout = 0

    for i in range(10):
        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)
        
        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        avg_xout += accel_xout_scaled
        avg_yout += accel_yout_scaled
        avg_zout += accel_zout_scaled

    avg_xout = avg_xout / 10.0
    avg_yout = avg_yout / 10.0
    avg_zout = avg_zout / 10.0
    

    data = {
        # 'x_rotation' : get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled),
        # 'y_rotation' : get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        'x_rotation' : get_x_rotation(avg_xout, avg_yout, avg_zout),
        'y_rotation' : get_y_rotation(avg_xout, avg_yout, avg_zout)
        
    }

    response = config_response(data)

    return response

@app.route('/toggle_motor')
def toggle_motor():
    global motor_status

    if motor_status == 1:
        data = {
            'message': "Can't toggle motor when in use."
        }
        response = config_response(data, 409)
        return response

    duration = request.args.get('duration')
    toggle_on_off(float(duration), True)

    data = {
        'status': 1,
        'duration': duration
    }

    response = config_response(data)

    return response


@app.route('/motor_on')
def motor_on():
    global CHANNEL_MOTOR_ENABLE, motor_status

    pin_on(CHANNEL_MOTOR_ENABLE, 0)
    motor_status = 1

    data = {
        'motor_status': motor_status,
    }

    response = config_response(data)

    return response

@app.route('/motor_off')
def motor_off():
    global CHANNEL_MOTOR_ENABLE, motor_status

    pin_off(CHANNEL_MOTOR_ENABLE, 1)
    motor_status = 0

    data = {
        'motor_status': motor_status,
    }

    response = config_response(data)

    return response

@app.route('/current_direction')
def get_current_direction():
    global current_direction

    data = {
        'current_direction': current_direction
    }

    response = config_response(data)

    return response

@app.route('/change_direction')
def change_direction():
    global current_direction, motor_status

    if motor_status == 1:
        data = {
            'message': "Can't change direction when motor is on"
        }
        response = config_response(data, 409)
        return response

    if current_direction == 1: 
        set_motor_down()
        current_direction = 0
    else: 
        set_motor_up()
        current_direction = 1

    data = {
        'current_direction': current_direction
    }

    response = config_response(data)

    return response

@app.route('/get_averages')
def get_averages():
    global CHANNEL_MOTOR_ENABLE, motor_status
    if (motor_status == 1):
        data = {
            'message': "Can't get averages when motor is on"
        }
        response = config_response(data, 409)
        return response
    
    pin_on(CHANNEL_MOTOR_ENABLE, 0)
    motor_status = 1

    start_time = time()
    lapsed_time = time() - start_time
    averages = []

    while lapsed_time < 80:
        sleep(1)
        averages.append(mpu_average())
        lapsed_time = time() - start_time

    pin_off(CHANNEL_MOTOR_ENABLE, 1)
    motor_status = 0

    data = {
        'averages': averages,
        'motor_status': motor_status
    }

    response = config_response(data)

    return response

if __name__ == "__main__":
    print("running from main")
    signal.signal(signal.SIGINT, on_exit)
    main()
else:
    print('running from flask')
    signal.signal(signal.SIGINT, on_exit)
    
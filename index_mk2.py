#!/usr/bin/python

import RPi.GPIO as GPIO
import math
from flask import Flask, jsonify, make_response, request
import sys
import signal
from time import sleep, time
from os import path
from mpu6050 import mpu6050
import numpy as np
from scipy.optimize import curve_fit

MPU_ADDRESS = 0x68 # This is the MPU_ADDRESS value read via the i2cdetect command
CAL_SIZE = 1000 # Total number of samples to make calibration
ACCEL_CAL_DIR = './accel_cal.txt'

sensor = mpu6050(MPU_ADDRESS)

app = Flask(__name__)

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

def accel_fit(x_input, m_x, b)->float:
    return (m_x * x_input) + b

def get_accel()->tuple[float, float, float]:
    data = sensor.get_accel_data(True)
    return data['x'], data['y'], data['z']

def acceleration_calibration():
    print('-'*50)
    print('Accelerometer Calibration')
    #  mpu_offsets = [[x], [y], [z]]
    mpu_offsets = [[], [], []]
    axis_vec = ['z', 'y', 'x']
    cal_directions = ['upward', 'downward', 'perpendicular to gravity']
    cal_index = [2, 1, 0]
    for qq,ax_qq in enumerate(axis_vec):
        ax_offsets = [[], [], []]
        print('-'*50)
        for direc_ii,direc in enumerate(cal_directions):
            print('-'*8, 'Press Enter and keep MPU steady to calibrate the accelerometer with the -', ax_qq, 'axis pointed', direc)
            input()
            [get_accel() for ii in range(CAL_SIZE)]
            mpu_array = []
            while len(mpu_array) < CAL_SIZE:
                try:
                    ax,ay,az = get_accel()
                    mpu_array.append([ax, ay, az])
                except: continue
            ax_offsets[direc_ii] = np.array(mpu_array)[:, cal_index[qq]]
        
        popts,_ = curve_fit(
                    accel_fit,
                    np.append(
                        np.append(
                            ax_offsets[0],
                            ax_offsets[1]
                        ),
                        ax_offsets[2]
                    ),
                    np.append(
                        np.append(
                            1.0*np.ones(
                                np.shape(ax_offsets[0])
                            ),
                            -1.0*np.ones(
                                np.shape(ax_offsets[1])
                            )
                        ),
                        0.0*np.ones(
                            np.shape(ax_offsets[2])
                        )
                    ),
                    maxfev=10000
                )
        #  mpu_offsets = [[x], [y], [z]]
        mpu_offsets[cal_index[qq]] = popts
    print('Accelerometer Calibration')
    return mpu_offsets

def mpu_average():
    global accel_cal
    avg_xout = 0
    avg_yout = 0
    avg_zout = 0

    for i in range(10):
        ax, ay, az = get_accel()
        if accel_cal is not None:
            ax = accel_fit(ax, *accel_cal[0])
            ay = accel_fit(ay, *accel_cal[1])
            az = accel_fit(az, *accel_cal[2])

        avg_xout += ax
        avg_yout += ay
        avg_zout += az

    avg_xout = avg_xout / 10.0
    avg_yout = avg_yout / 10.0
    avg_zout = avg_zout / 10.0

    return avg_xout, avg_yout, avg_zout

def config_response(data, status=200):
    response = make_response(jsonify(data), status)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'

    return response

@app.route('/')
def index():
    global CHANNEL_MOTOR_ENABLE, current_direction, motor_status, accel_cal

    # Get calibration offsets from ./accel_cal.txt
    accel_cal = None
    if path.exists(ACCEL_CAL_DIR):
        with open(ACCEL_CAL_DIR, 'r') as file:
            lines = file.readlines()
            accel_cal = [np.array([float(value) for value in line.replace('\n','').split(',')]) for line in lines]

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
    avg_xout, avg_yout, avg_zout = mpu_average()

    data = {
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
        averages.append(mpu_average())
        lapsed_time = time() - start_time
        sleep(1)

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
else:
    print('running from flask')
    signal.signal(signal.SIGINT, on_exit)
    
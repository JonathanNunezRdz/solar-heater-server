#!/usr/bin/python

from flask import Flask, jsonify, make_response, request, Response
import signal
from time import sleep, time
from mpu6050 import mpu6050

MPU_ADDRESS = 0x68 # This is the MPU_ADDRESS value read via the i2cdetect command
sensor = mpu6050(MPU_ADDRESS)

from rotation_functions import get_x_rotation, get_y_rotation
from gpio_functions import setup_gpio, on_exit
from acceleration_functions import get_accel_dict, get_cal, mpu_average
from motor_functions import toggle_on_off, set_motor_down, set_motor_up, setup_motor


CAL_SIZE = 1000 # Total number of samples to make calibration
ACCEL_CAL_DIR = './accel_cal.txt'
CHANNEL_MOTOR_ENABLE = 25
CHANNEL_MOTOR_IN_1 = 23
CHANNEL_MOTOR_IN_2 = 24


app = Flask(__name__)

def config_response(data:dict, status:int=200)->Response:
    response = make_response(jsonify(data), status)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/')
def index():
    global accel_cal, motor_duty_cycle, current_direction, motor_status, motor
    # Get calibration offsets
    accel_cal = get_cal()
    
    # initialize duty cycle for L298N - PWM
    motor_duty_cycle = 25

    # initialize direction to upwards
    current_direction = 'up'

    # initialize motor to off
    motor_status = 0

    # list to set as outputs
    channel_list = [CHANNEL_MOTOR_ENABLE, CHANNEL_MOTOR_IN_1, CHANNEL_MOTOR_IN_2]

    # set channels to outout
    setup_gpio(channel_list)

    # initialize motor 
    motor = setup_motor()

    data = {
        'status': 1,
        'message': 'setup complete'
    }
    response = config_response(data)
    return response

@app.route('/mpu')
def mpu():
    global accel_cal
    avg_xout, avg_yout, avg_zout = mpu_average(accel_cal)

    data = {
        'x_rotation' : get_x_rotation(avg_xout, avg_yout, avg_zout),
        'y_rotation' : get_y_rotation(avg_xout, avg_yout, avg_zout)
    }
    response = config_response(data)
    return response

@app.route('/toggle_motor')
def toggle_motor():
    global motor_status, motor, motor_duty_cycle

    if motor_status == 1:
        data = {
            'message': "Can't toggle motor when in use."
        }
        response = config_response(data, 409)
        return response

    duration = request.args.get('duration')
    toggle_on_off(motor, motor_duty_cycle, float(duration), True)

    data = {
        'status': 1,
        'duration': duration
    }
    response = config_response(data)
    return response


@app.route('/motor_on')
def motor_on():
    global motor_status, motor, motor_duty_cycle, current_direction

    if motor_status == 1:
        data = {
            'message': 'Motor is already on',
            'status': 0
        }
        response = config_response(data, 409)
        return response

    motor.start(motor_duty_cycle)
    motor_status = 1

    data = {
        'motor_status': motor_status,
        'current_direction': current_direction
    }
    response = config_response(data)
    return response

@app.route('/motor_off')
def motor_off():
    global motor_status, motor

    if motor_status == 0:
        data = {
            'message': 'Motor is already off',
            'status': 0
        }
        response = config_response(data, 409)
        return response

    motor.stop()
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

    if current_direction == 'up': 
        set_motor_down()
        current_direction = 'down'
    else: 
        set_motor_up()
        current_direction = 'up'

    data = {
        'current_direction': current_direction
    }
    response = config_response(data)
    return response

@app.route('/get_averages')
def get_averages():
    global CHANNEL_MOTOR_ENABLE, motor_status, motor, motor_duty_cycle, accel_cal
    if motor_status == 1:
        data = {
            'message': "Can't get averages when motor is on"
        }
        response = config_response(data, 409)
        return response
    
    motor.start(motor_duty_cycle)
    motor_status = 1

    start_time = time()
    lapsed_time = time() - start_time
    averages = []

    while lapsed_time < 80:
        averages.append(get_accel_dict(*mpu_average(accel_cal)))
        lapsed_time = time() - start_time
        sleep(1)

    motor.stop()
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
    
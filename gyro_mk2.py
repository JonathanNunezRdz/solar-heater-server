from time import sleep, time
from mpu6050 import mpu6050
import threading as th
import csv
import numpy as np
from scipy.optimize import curve_fit

sensor = mpu6050(0x68)
# sensor.set_gyro_range(sensor.GYRO_RANGE_2000DEG)
# sensor.set_accel_range(sensor.ACCEL_RANGE_16G)
# start_time = time()

accel_range = {
    '2': sensor.ACCEL_RANGE_2G,
    '4': sensor.ACCEL_RANGE_4G,
    '8': sensor.ACCEL_RANGE_8G,
    '16': sensor.ACCEL_RANGE_16G,
}

gyro_range = {
    '250': sensor.GYRO_RANGE_250DEG,
    '500': sensor.GYRO_RANGE_500DEG,
    '1000': sensor.GYRO_RANGE_1000DEG,
    '2000': sensor.GYRO_RANGE_2000DEG,
}

CAL_SIZE = 100

def accel_fit(x_input, m_x, b):
    return (m_x*x_input)+b

def acceleration_calibration():
    print('-'*50)
    print('Accelerometer Calibration')
    mpu_offsets = [[], [], []]
    axis_vec = ['z', 'y', 'x']
    cal_directions = ['upward', 'downward', 'perpendicular to gravity']
    cal_index = [2, 1, 0]
    for qq,ax_qq in enumerate(axis_vec):
        ax_offsets = [[], [], []]
        print('-'*50)
        for direc_ii,direc in enumerate(cal_directions):
            input('-'*8, 'Press Enter and keep MPU steady to calibrate the accelerometer with the -', ax_qq, 'axis pointed', direc)
            [sensor.get_accel_data(True) for ii in range(CAL_SIZE)]
            mpu_array = []
            while len(mpu_array) < CAL_SIZE:
                try:
                    data = sensor.get_accel_data(True)
                    ax, ay, az = data['x'], data['y'], data['z']
                    mpu_array.append([ax, ay, az])
                except: continue
            ax_offsets[direc_ii] = np.array(mpu_array)[:, cal_index[qq]]
        
        popts, = curve_fit(accel_fit,np.append(np.append(ax_offsets[0],
                                 ax_offsets[1]),ax_offsets[2]),
                   np.append(np.append(1.0*np.ones(np.shape(ax_offsets[0])),
                    -1.0*np.ones(np.shape(ax_offsets[1]))),
                        0.0*np.ones(np.shape(ax_offsets[2]))),
                            maxfev=10000)
        
        mpu_offsets[cal_index[qq]] = popts
    print('Accelerometer Calibration')
    return mpu_offsets

def key_capture_thread():
    global keep_going
    input()
    keep_going = False

def acceleration_loop():
    global keep_going
    print('accel range', sensor.read_accel_range())

    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    
    while keep_going:
        sleep(0.1)
        data = sensor.get_accel_data(True)
        data['x'] = round(data['x'], 2)
        data['y'] = round(data['y'], 2)
        data['z'] = round(data['z'], 2)
        print(data)

    return None


def set_acceleration(range='2'):
    sensor.set_accel_range(accel_range[range])

def main():
    global keep_going
    loop = True
    while(loop):
        keep_going = True
        print('Option A - acceleration')
        print('Option B - calibrate accelerometer')
        print('Optino C - set range')
        option = input()
        if option == 'A': acceleration_loop()
        elif option == 'B': acceleration_calibration()
        elif option == 'C':
            print('Option A - set acceleration range')
            option = input()
            if option == 'A':
                print('Option 2 - 2G')
                print('Option 4 - 4G')
                print('Option 8 - 8G')
                print('Option 16 - 16G')
                option = input()
                if option in ['2', '4', '8', '16']: set_acceleration(option)
                else: exit(2)
        print('Do you want to continue - (y/n)')
        option = input()
        if (option == 'n'): loop = False

if __name__ == '__main__':
    main()

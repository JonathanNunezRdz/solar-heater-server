import numpy as np
from scipy.optimize import curve_fit
from index_mk2 import CAL_SIZE, ACCEL_CAL_DIR

def get_accel_dict(ax:float, ay:float, az:float):
    return {
        'ax': ax,        
        'ay': ay,
        'az': az,
    }

def get_cal()->list[np.ndarray]:
    with open(ACCEL_CAL_DIR, 'r') as file:
        lines = file.readlines()
        return [np.array([float(value) for value in line.replace('\n','').split(',')]) for line in lines]

def mpu_average(accel_cal:list[np.ndarray], sensor)->tuple[float, float, float]:
    avg_xout = 0
    avg_yout = 0
    avg_zout = 0

    for i in range(10):
        ax, ay, az = get_accel(sensor)
        if len(accel_cal) > 0:
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


def accel_fit(x_input, m_x, b)->float:
    return (m_x*x_input) + b

def get_accel(sensor)->tuple[float, float, float]:
    data = sensor.get_accel_data(True)
    return data['x'], data['y'], data['z']

def acceleration_calibration(sensor):
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
            [get_accel(sensor) for ii in range(CAL_SIZE)]
            mpu_array = []
            while len(mpu_array) < CAL_SIZE:
                try:
                    ax,ay,az = get_accel(sensor)
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
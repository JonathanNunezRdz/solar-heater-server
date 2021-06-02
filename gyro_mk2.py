from time import sleep, time
from mpu6050 import mpu6050
import threading as th
import csv

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

def key_capture_thread():
    global keep_going
    input()
    keep_going = False

def acceleration_loop():
    global keep_going
    print('accel range', sensor.read_accel_range())
    # th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    # avg_list =[]
    # while keep_going:
    #     sleep(0.1)
    #     data = sensor.get_accel_data()
    #     avg_list.append(data)
    #     print(data)
    # print('\n')
    # avg_x = 0
    # avg_y = 0
    # avg_z = 0
    # for data in avg_list:
    #     avg_x += data['x']
    #     avg_y += data['y']
    #     avg_z += data['z']
    # avg_x = avg_x / len(avg_list)
    # avg_y = avg_y / len(avg_list)
    # avg_z = avg_z / len(avg_list)

    # get 500 samples to calibrate acceleration
    # avg_list = [sensor.get_accel_data() for _ in range(500)]
    # avg_x = 0.0
    # avg_y = 0.0
    # avg_z = 0.0
    # for data in avg_list:
    #     avg_x += round(data['x'], 2)
    #     avg_y += round(data['y'], 2)
    #     avg_z += round(data['z'], 2)
    # avg_x = round((avg_x / 200), 2)
    # avg_y = round((avg_y / 200), 2)
    # avg_z = round((avg_z / 200), 2)
    
    # print('calibrated', {'x': avg_x, 'y': avg_y, 'z': avg_z})

    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    avg_list_calibrated = []
    while keep_going:
        sleep(0.1)
        data = sensor.get_accel_data(True)
        # data_calibrated = {
        #     'x': round(data['x'] - avg_x, 2),
        #     'y': round(data['y'] - avg_y, 2),
        #     'z': round(data['z'] - avg_z, 2)
        # }
        # avg_list_calibrated.append(data_calibrated)
        print(data)

    return None

def gyroscope_loop():
    global keep_going
    print('gyro range', sensor.read_gyro_range())
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()

    # get 200 samples to calibrate
    # for i in range(200):
    #     data = sensor.get_
    average_list = []
    while keep_going:
        sleep(0.1)
        data = sensor.get_gyro_data()
        average_list.append(data)
        print(data)
    print('\n')
    avg_x = 0
    avg_y = 0
    avg_z = 0
    for data in average_list:
        avg_x += data['x']
        avg_y += data['y']
        avg_z += data['z']
    avg_x = avg_x / len(average_list)
    avg_y = avg_y / len(average_list)
    avg_z = avg_z / len(average_list)
    print({'x': avg_x, 'y': avg_y, 'z': avg_z})
    return None

def set_acceleration(range='2'):
    sensor.set_accel_range(accel_range[range])

def set_gyroscope(range='250'):
    sensor.set_gyro_range(gyro_range[range])

def main():
    global keep_going
    loop = True
    while(loop):
        keep_going = True
        print('Option A - acceleration')
        print('Option B - gyroscope')
        print('Optino C - set ranges')
        option = input()
        if option == 'A': acceleration_loop()
        elif option == 'B': gyroscope_loop()
        elif option == 'C':
            print('Option A - set acceleration range')
            print('Option B - set gyroscope range')
            option = input()
            if option == 'A':
                print('Option 2 - 2G')
                print('Option 4 - 4G')
                print('Option 8 - 8G')
                print('Option 16 - 16G')
                option = input()
                if option in ['2', '4', '8', '16']: set_acceleration(option)
                else: exit(2)
            elif option == 'B':
                print('Option 250 - 250DEG')
                print('Option 500 - 500DEG')
                print('Option 1000 - 1000DEG')
                print('Option 2000 - 2000DEG')
                option = input()
                if option in ['250', '500', '1000', '2000']: set_gyroscope(option)
                else: exit(2)
        print('Do you want to continue - (y/n)')
        option = input()
        if (option == 'n'): loop = False

if __name__ == '__main__':
    main()


# with open('module_data.csv', mode='w') as csv_file:
#     fieldnames = ['time_lapsed', 'accel_x', 'accel_y', 'accel_z', 'gyro_x', 'gyro_y', 'gyro_z']
#     writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#     writer.writeheader()
#     while True:
#         # do something
#         accel_data = sensor.get_accel_data()
#         gyro_data = sensor.get_gyro_data()
#         time_lapsed = time() - start_time
#         accel_x = accel_data['x']
#         accel_y = accel_data['y']
#         accel_z = accel_data['z']
#         gyro_x = gyro_data['x']
#         gyro_y = gyro_data['y']
#         gyro_z = gyro_data['z']
#         writer.writerow({'time_lapsed': time_lapsed, 'accel_x': accel_x, 'accel_y': accel_y, 'accel_z': accel_z, 'gyro_x': gyro_x, 'gyro_y': gyro_y, 'gyro_z': gyro_z })
#         sleep(1)

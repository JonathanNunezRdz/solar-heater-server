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

keep_going = True
def key_capture_thread():
    global keep_going
    input()
    keep_going = False

def acceleration_loop():
    print('accel range', sensor.read_accel_range())
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    while keep_going:
        print(sensor.get_accel_data())
    print('\n')
    return None

def gyroscope_loop():
    print('gyro range', sensor.read_gyro_range())
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    while keep_going:
        print(sensor.get_gyro_data())
    print('\n')
    return None

def set_acceleration(range='2'):
    sensor.set_accel_range(accel_range[range])

def set_gyroscope(range='250'):
    sensor.set_gyro_range(gyro_range[range])

def main():
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

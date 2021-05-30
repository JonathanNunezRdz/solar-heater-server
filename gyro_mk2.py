from time import sleep, time
from mpu6050 import mpu6050
import csv

sensor = mpu6050(0x68)
sensor.set_gyro_range(sensor.GYRO_RANGE_2000DEG)
# sensor.set_accel_range(sensor.ACCEL_RANGE_16G)
# print('accel range', sensor.read_accel_range())
print('gyro_range', sensor.read_gyro_range())
# start_time = time()


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

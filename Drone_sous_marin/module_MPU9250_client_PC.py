#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import math
import quaternion_filters

##enum Ascale, accelerometer modes
AFS_2G  = 0
AFS_4G  = 1
AFS_8G  = 2
AFS_16G = 3

##enum Gscale, gyrometer modes
GFS_250DPS  = 0
GFS_500DPS  = 1
GFS_1000DPS = 2
GFS_2000DPS = 3

##enum Mscale, magnetometer modes
MFS_14BITS = 0 # 0.6 mG per LSB
MFS_16BITS = 1 # 0.15 mG per LSB

##enum M_MODE
M_8HZ   = 0x02  # 8 Hz update
M_100HZ = 0x06 # 100 Hz continuous magnetometer

data_values = None

def getAres(Ascale):
    ## Possible accelerometer scales (and their register bit settings) are:
    ## 2 Gs (00), 4 Gs (01), 8 Gs (10), and 16 Gs  (11).
    ## Here's a bit of an algorith to calculate DPS/(ADC tick) based on that
    ## 2-bit value:
    if Ascale == AFS_2G:
        aRes = 2.0 / 32768.0
    if Ascale == AFS_4G:
        aRes = 4.0 / 32768.0
    if Ascale == AFS_8G:
        aRes = 8.0 / 32768.0
    if Ascale == AFS_16G:
        aRes = 16.0 / 32768.0

    return aRes

def getGres(Gscale):
    ## Possible gyro scales (and their register bit settings) are:
    ## 250 DPS (00), 500 DPS (01), 1000 DPS (10), and 2000 DPS (11).
    ## Here's a bit of an algorith to calculate DPS/(ADC tick) based on that
    ## 2-bit value:
    if Gscale == GFS_250DPS:
        gRes = 250.0 / 32768.0
    if Gscale == GFS_500DPS:
        gRes = 500.0 / 32768.0
    if Gscale == GFS_1000DPS:
        gRes = 1000.0 / 32768.0
    if Gscale == GFS_2000DPS:
        gRes = 2000.0 / 32768.0

    return gRes

def getMres(Mscale):
    ## Possible magnetometer scales (and their register bit settings) are:
    ## 14 bit resolution (0) and 16 bit resolution (1)
    if Mscale == MFS_14BITS:
        mRes = 10.0 * 4912.0 / 8190.0 # Proper scale to return milliGauss
    if Mscale == MFS_16BITS:
        mRes = 10.0 * 4912.0 / 32760.0 # Proper scale to return milliGauss

    return mRes

def compute_Compass_Heading(mx, my):
    ## just heading = math.atan2(mx, -my) for heading angle from -180° to 180°
    if (my == 0):
        if mx < 0 :
            heading = math.pi
        else:
            heading = 0
    else:
        heading = math.atan2(mx, my)

    if mx == 0:
        if my > 0:
            heading = 0
        if my < 0:
            heading = math.pi

    if my == 0:
        if mx > 0:
            heading = -math.pi / 2
        if mx < 0:
            heading = math.pi / 2

    if (heading > math.pi):
        heading = heading - 2 * math.pi
    elif (heading < -math.pi):
        heading = heading + 2 * math.pi
    elif (heading < 0):
        heading = heading + 2 * math.pi

    heading = heading * 180.0 / math.pi

    return heading

def process_data(data):
    global data_values

    t, delta_t = int(data[0]), int(data[1])
    tempRaw = int(data[2])
    accelRaw = [int(data[3]), int(data[4]), int(data[5])]
    gyroRaw = [int(data[6]), int(data[7]), int(data[8])]
    magRaw = [float(data[9]), float(data[10]), float(data[11])]
    factoryMagCalibration = [int(data[12]), int(data[13]), int(data[14])]
    Ascale, Gscale, Mscale, Mmode = int(data[15]), int(data[16]), int(data[17]), int(data[18])

    aRes = getAres(Ascale)
    gRes = getGres(Gscale)
    mRes = getMres(Mscale)

    scaled_factoryMagCalibration = [(factoryMagCalibration[0] - 128) / 256 + 1, (factoryMagCalibration[1] - 128) / 256 + 1, (factoryMagCalibration[2] - 128) / 256 + 1]
    accel_values = [accelRaw[0] * aRes, accelRaw[1] * aRes, accelRaw[2] * aRes]
    gyro_values = [gyroRaw[0] * gRes, gyroRaw[1] * gRes, gyroRaw[2] * gRes]
    mag_values = [magRaw[0] * scaled_factoryMagCalibration[0] * mRes, magRaw[1] * scaled_factoryMagCalibration[1] * mRes, magRaw[2] * scaled_factoryMagCalibration[2] * mRes]
    temp_value = tempRaw / 333.87 + 21.0
    heading = compute_Compass_Heading(mag_values[1], mag_values[0])
    quat_values = quaternion_filters.mahony_Q6_Update(accel_values[0], accel_values[1], accel_values[2], gyro_values[0] * math.pi / 180, gyro_values[1] * math.pi / 180, gyro_values[2] * math.pi / 180, t / 1000000) # t must be in ms

    data_values = [t, delta_t, accel_values, gyro_values, mag_values, quat_values, temp_value, heading]

def main():
    pass

if __name__ == '__main__':
    main()

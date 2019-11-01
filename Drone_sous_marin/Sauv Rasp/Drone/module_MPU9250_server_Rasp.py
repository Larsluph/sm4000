#!/usr/bin/env python
# -*- coding: utf-8 -*-

## MPU9250 Basic Example Code
## by: Kris Winer
## date: April 1, 2014
## license: Beerware - Use this code however you'd like. If you
## find it useful you can buy me a beer some time.
## Modified by Brent Wilkins July 19, 2016
## Modified by Stephane Ramstein October 25, 2018 for Python use with Raspberry Pi,
##       without classes, i2c only
##
## Demonstrate basic MPU-9250 functionality including parameterizing the register
## addresses, initializing the sensor, getting properly scaled accelerometer,
## gyroscope, and magnetometer data out. Added display functions to allow display
## to on breadboard monitor. Addition of 9 DoF sensor fusion using open source
## Madgwick and Mahony filter algorithms. Sketch runs on the 3.3 V 8 MHz Pro Mini
## and the Teensy 3.1.
##
## SDA and SCL should have external pull-up resistors (to 3.3V).
## 10k resistors are on the EMSENSR-9250 breakout board.
##
## Hardware setup:
## MPU9250 Breakout --------- Arduino
## VDD ---------------------- 3.3V
## VDDI --------------------- 3.3V
## SDA ----------------------- A4
## SCL ----------------------- A5
## GND ---------------------- GND
## 
## See also MPU-9250 Register Map and Descriptions, Revision 4.0,
## RM-MPU-9250A-00, Rev. 1.4, 9/9/2013 for registers not listed in above
## document; the MPU9250 and MPU9150 are virtually identical but the latter has
## a different register map

import smbus
import time
import keyboard
import socket

## Magnetometer Registers
WHO_AM_I_AK8963  = 0x00 # (AKA WIA) should return 0x48
INFO             = 0x01
AK8963_ST1       = 0x02 # data ready status bit 0
AK8963_XOUT_L    = 0x03 # data
AK8963_XOUT_H    = 0x04
AK8963_YOUT_L    = 0x05
AK8963_YOUT_H    = 0x06
AK8963_ZOUT_L    = 0x07
AK8963_ZOUT_H    = 0x08
AK8963_ST2       = 0x09 # Data overflow bit 3 and data read error status bit 2
AK8963_CNTL      = 0x0A # Power down (0000), single-measurement (0001), self-test (1000) and Fuse ROM (1111) modes on bits 3:0
AK8963_ASTC      = 0x0C # Self test control
AK8963_I2CDIS    = 0x0F # I2C disable
AK8963_ASAX      = 0x10 # Fuse ROM x-axis sensitivity adjustment value
AK8963_ASAY      = 0x11 # Fuse ROM y-axis sensitivity adjustment value
AK8963_ASAZ      = 0x12 # Fuse ROM z-axis sensitivity adjustment value

## Accelerometer and gyrometer Registers
SELF_TEST_X_GYRO = 0x00
SELF_TEST_Y_GYRO = 0x01
SELF_TEST_Z_GYRO = 0x02

##X_FINE_GAIN      = 0x03 # [7:0] fine gain
##Y_FINE_GAIN      = 0x04
##Z_FINE_GAIN      = 0x05
##XA_OFFSET_H      = 0x06 # User-defined trim values for accelerometer
##XA_OFFSET_L_TC   = 0x07
##YA_OFFSET_H      = 0x08
##YA_OFFSET_L_TC   = 0x09
##ZA_OFFSET_H      = 0x0A
##ZA_OFFSET_L_TC   = 0x0B

SELF_TEST_X_ACCEL = 0x0D
SELF_TEST_Y_ACCEL = 0x0E
SELF_TEST_Z_ACCEL = 0x0F

SELF_TEST_A       = 0x10

XG_OFFSET_H       = 0x13 # User-defined trim values for gyroscope
XG_OFFSET_L       = 0x14
YG_OFFSET_H       = 0x15
YG_OFFSET_L       = 0x16
ZG_OFFSET_H       = 0x17
ZG_OFFSET_L       = 0x18
SMPLRT_DIV        = 0x19
CONFIG            = 0x1A
GYRO_CONFIG       = 0x1B
ACCEL_CONFIG      = 0x1C
ACCEL_CONFIG2     = 0x1D
LP_ACCEL_ODR      = 0x1E
WOM_THR           = 0x1F

## Duration counter threshold for motion interrupt generation, 1 kHz rate,
## LSB = 1 ms
MOT_DUR           = 0x20
## Zero-motion detection threshold bits [7:0]
ZMOT_THR          = 0x21
## Duration counter threshold for zero motion interrupt generation, 16 Hz rate,
## LSB = 64 ms
ZRMOT_DUR         = 0x22

FIFO_EN            = 0x23
I2C_MST_CTRL       = 0x24
I2C_SLV0_ADDR      = 0x25
I2C_SLV0_REG       = 0x26
I2C_SLV0_CTRL      = 0x27
I2C_SLV1_ADDR      = 0x28
I2C_SLV1_REG       = 0x29
I2C_SLV1_CTRL      = 0x2A
I2C_SLV2_ADDR      = 0x2B
I2C_SLV2_REG       = 0x2C
I2C_SLV2_CTRL      = 0x2D
I2C_SLV3_ADDR      = 0x2E
I2C_SLV3_REG       = 0x2F
I2C_SLV3_CTRL      = 0x30
I2C_SLV4_ADDR      = 0x31
I2C_SLV4_REG       = 0x32
I2C_SLV4_DO        = 0x33
I2C_SLV4_CTRL      = 0x34
I2C_SLV4_DI        = 0x35
I2C_MST_STATUS     = 0x36
INT_PIN_CFG        = 0x37
INT_ENABLE         = 0x38
DMP_INT_STATUS     = 0x39 # Check DMP interrupt
INT_STATUS         = 0x3A
ACCEL_XOUT_H       = 0x3B
ACCEL_XOUT_L       = 0x3C
ACCEL_YOUT_H       = 0x3D
ACCEL_YOUT_L       = 0x3E
ACCEL_ZOUT_H       = 0x3F
ACCEL_ZOUT_L       = 0x40
TEMP_OUT_H         = 0x41
TEMP_OUT_L         = 0x42
GYRO_XOUT_H        = 0x43
GYRO_XOUT_L        = 0x44
GYRO_YOUT_H        = 0x45
GYRO_YOUT_L        = 0x46
GYRO_ZOUT_H        = 0x47
GYRO_ZOUT_L        = 0x48
EXT_SENS_DATA_00   = 0x49
EXT_SENS_DATA_01   = 0x4A
EXT_SENS_DATA_02   = 0x4B
EXT_SENS_DATA_03   = 0x4C
EXT_SENS_DATA_04   = 0x4D
EXT_SENS_DATA_05   = 0x4E
EXT_SENS_DATA_06   = 0x4F
EXT_SENS_DATA_07   = 0x50
EXT_SENS_DATA_08   = 0x51
EXT_SENS_DATA_09   = 0x52
EXT_SENS_DATA_10   = 0x53
EXT_SENS_DATA_11   = 0x54
EXT_SENS_DATA_12   = 0x55
EXT_SENS_DATA_13   = 0x56
EXT_SENS_DATA_14   = 0x57
EXT_SENS_DATA_15   = 0x58
EXT_SENS_DATA_16   = 0x59
EXT_SENS_DATA_17   = 0x5A
EXT_SENS_DATA_18   = 0x5B
EXT_SENS_DATA_19   = 0x5C
EXT_SENS_DATA_20   = 0x5D
EXT_SENS_DATA_21   = 0x5E
EXT_SENS_DATA_22   = 0x5F
EXT_SENS_DATA_23   = 0x60
MOT_DETECT_STATUS  = 0x61
I2C_SLV0_DO        = 0x63
I2C_SLV1_DO        = 0x64
I2C_SLV2_DO        = 0x65
I2C_SLV3_DO        = 0x66
I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET  = 0x68
MOT_DETECT_CTRL    = 0x69
USER_CTRL          = 0x6A # Bit 7 enable DMP, bit 3 reset DMP
PWR_MGMT_1         = 0x6B # Device defaults to the SLEEP mode
PWR_MGMT_2         = 0x6C
DMP_BANK           = 0x6D # Activates a specific bank in the DMP
DMP_RW_PNT         = 0x6E # Set read/write pointer to a specific start address in specified DMP bank
DMP_REG            = 0x6F # Register in DMP from which to read or to which to write
DMP_REG_1          = 0x70
DMP_REG_2          = 0x71
FIFO_COUNTH        = 0x72
FIFO_COUNTL        = 0x73
FIFO_R_W           = 0x74
WHO_AM_I_MPU9250   = 0x75 # Should return = 0x71
XA_OFFSET_H        = 0x77
XA_OFFSET_L        = 0x78
YA_OFFSET_H        = 0x7A
YA_OFFSET_L        = 0x7B
ZA_OFFSET_H        = 0x7D
ZA_OFFSET_L        = 0x7E

MPU9250_ADDRESS    = 0x68 # Device address when ADO = 0. if AD0 = 1 0x69
AK8963_ADDRESS     = 0x0C

READ_FLAG          = 0x80

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

## Specify default sensor full scale
Gscale = GFS_2000DPS
Ascale = AFS_2G
Mscale = MFS_16BITS
Mmode = M_8HZ

def stop_running():
    global running

    running = False

def uint_16_to_int16(val): # convert unsigned 16 bit integers into signed ones.
    if (val >= 0x8000):
        return -((0xFFFF - val) + 1)
    else:
        return val

def MPU9250SelfTest():
    global bus
    aAvg = [0, 0, 0]
    gAvg = [0, 0, 0]
    aSTAvg = [0, 0, 0]
    gSTAvg = [0, 0, 0]
    selfTest = [0, 0, 0, 0, 0, 0]
    factoryTrim = [0, 0, 0, 0, 0, 0]
    destination  = [0, 0, 0, 0, 0, 0]
    FS = 0
    
    ## Set gyro sample rate to 1 kHz
    bus.write_byte_data(MPU9250_ADDRESS, SMPLRT_DIV, 0x00)
    ## Set gyro sample rate to 1 kHz and DLPF to 92 Hz
    bus.write_byte_data(MPU9250_ADDRESS, CONFIG, 0x02);
    ## Set full scale range for the gyro to 250 dps
    bus.write_byte_data(MPU9250_ADDRESS, GYRO_CONFIG, 1<<FS);
    ## Set accelerometer rate to 1 kHz and bandwidth to 92 Hz
    bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG2, 0x02);
    ## Set full scale range for the accelerometer to 2 g
    bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG, 1<<FS);

    ## Get average current values of gyro and acclerometer
    for ii in range(200):
        ## Read the six raw data registers sequentially into data array
        rawData = bus.read_i2c_block_data(MPU9250_ADDRESS, ACCEL_XOUT_H, 6)
        ## Turn the MSB and LSB into a signed 16-bit value
        aAvg[0] += uint_16_to_int16((rawData[0] << 8) | rawData[1])
        aAvg[1] += uint_16_to_int16((rawData[2] << 8) | rawData[3])
        aAvg[2] += uint_16_to_int16((rawData[4] << 8) | rawData[5])

        ## Read the six raw data registers sequentially into data array
        rawData = bus.read_i2c_block_data(MPU9250_ADDRESS, GYRO_XOUT_H, 6)
        ## Turn the MSB and LSB into a signed 16-bit value
        gAvg[0] += uint_16_to_int16((rawData[0] << 8) | rawData[1])
        gAvg[1] += uint_16_to_int16((rawData[2] << 8) | rawData[3])
        gAvg[2] += uint_16_to_int16((rawData[4] << 8) | rawData[5])

    ## Get average of 200 values and store as average current readings
    for ii in range(3):
        aAvg[ii] /= 200
        gAvg[ii] /= 200

    ## Configure the accelerometer for self-test
    ## Enable self test on all three axes and set accelerometer range to +/- 2 g
    bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG, 0xE0);
    ## Enable self test on all three axes and set gyro range to +/- 250 degrees/s
    bus.write_byte_data(MPU9250_ADDRESS, GYRO_CONFIG,  0xE0);
    time.sleep(0.025) # Delay a while to let the device stabilize

    ## Get average self-test values of gyro and acclerometer
    for ii in range(200):
        ## Read the six raw data registers sequentially into data array
        rawData = bus.read_i2c_block_data(MPU9250_ADDRESS, ACCEL_XOUT_H, 6)
        ## Turn the MSB and LSB into a signed 16-bit value
        aSTAvg[0] += uint_16_to_int16((rawData[0] << 8) | rawData[1])
        aSTAvg[1] += uint_16_to_int16((rawData[2] << 8) | rawData[3])
        aSTAvg[2] += uint_16_to_int16((rawData[4] << 8) | rawData[5])
        
        ## Read the six raw data registers sequentially into data array
        rawData = bus.read_i2c_block_data(MPU9250_ADDRESS, GYRO_XOUT_H, 6)
        ## Turn the MSB and LSB into a signed 16-bit value
        gSTAvg[0] += uint_16_to_int16((rawData[0] << 8) | rawData[1])
        gSTAvg[1] += uint_16_to_int16((rawData[2] << 8) | rawData[3])
        gSTAvg[2] += uint_16_to_int16((rawData[4] << 8) | rawData[5])

    ## Get average of 200 values and store as average self-test readings
    for ii in range(3):
        aSTAvg[ii] /= 200
        gSTAvg[ii] /= 200
    
    ## Configure the gyro and accelerometer for normal operation
    bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG, 0x00)
    bus.write_byte_data(MPU9250_ADDRESS, GYRO_CONFIG,  0x00)
    time.sleep(0.025) # Delay a while to let the device stabilize

    ## Retrieve accelerometer and gyro factory Self-Test Code from USR_Reg
    ## X-axis accel self-test results
    selfTest[0] = bus.read_byte_data(MPU9250_ADDRESS, SELF_TEST_X_ACCEL)
    ## Y-axis accel self-test results
    selfTest[1] = bus.read_byte_data(MPU9250_ADDRESS, SELF_TEST_Y_ACCEL)
    ## Z-axis accel self-test results
    selfTest[2] = bus.read_byte_data(MPU9250_ADDRESS, SELF_TEST_Z_ACCEL)
    ## X-axis gyro self-test results
    selfTest[3] = bus.read_byte_data(MPU9250_ADDRESS, SELF_TEST_X_GYRO)
    ## Y-axis gyro self-test results
    selfTest[4] = bus.read_byte_data(MPU9250_ADDRESS, SELF_TEST_Y_GYRO)
    ## Z-axis gyro self-test results
    selfTest[5] = bus.read_byte_data(MPU9250_ADDRESS, SELF_TEST_Z_GYRO)

    ## Retrieve factory self-test value from self-test code reads
    ## FT[Xa] factory trim calculation
    factoryTrim[0] = (2620/(1<<FS))*1.01**(selfTest[0] - 1.0)
    ## FT[Ya] factory trim calculation
    factoryTrim[1] = (2620/(1<<FS))*1.01**(selfTest[1] - 1.0)
    ## FT[Za] factory trim calculation
    factoryTrim[2] = (2620/(1<<FS))*1.01**(selfTest[2] - 1.0)
    ## FT[Xg] factory trim calculation
    factoryTrim[3] = (2620/(1<<FS))*1.01**(selfTest[3] - 1.0)
    ## FT[Yg] factory trim calculation
    factoryTrim[4] = (2620/(1<<FS))*1.01**(selfTest[4] - 1.0)
    ## FT[Zg] factory trim calculation
    factoryTrim[5] = (2620/(1<<FS))*1.01**(selfTest[5] - 1.0)

    ## Report results as a ratio of (STR - FT)/FT; the change from Factory Trim
    ## of the Self-Test Response
    ## To get percent, must multiply by 100
    for i in range(3):
        ## Report percent differences
        destination[i] = 100.0 * (aSTAvg[i] - aAvg[i]) / factoryTrim[i] - 100.
        ## Report percent differences
        destination[i+3] = 100.0 * (gSTAvg[i] - gAvg[i]) / factoryTrim[i+3] - 100.

    return destination    

def calibrateMPU9250():
    ## Function which accumulates gyro and accelerometer data after device
    ## initialization. It calculates the average of the at-rest readings and then
    ## loads the resulting offsets into accelerometer and gyro bias registers.

    accelBias = [0, 0, 0]
    gyroBias = [0, 0, 0]
    accel_bias = [0, 0, 0]
    gyro_bias = [0, 0, 0]
    gyrosensitivity  = 131   # = 131 LSB/degrees/sec
    accelsensitivity = 16384 # = 16384 LSB/g

    ## reset device
    ## Write a one to bit 7 reset bit; toggle reset device
    bus.write_byte_data(MPU9250_ADDRESS, PWR_MGMT_1, READ_FLAG)
    time.sleep(0.1)

    ## get stable time source; Auto select clock source to be PLL gyroscope
    ## reference if ready else use the internal oscillator, bits 2:0 = 001
    bus.write_byte_data(MPU9250_ADDRESS, PWR_MGMT_1, 0x01)
    bus.write_byte_data(MPU9250_ADDRESS, PWR_MGMT_2, 0x00)
    time.sleep(0.2)

    ## Configure device for bias calculation
    ## Disable all interrupts
    bus.write_byte_data(MPU9250_ADDRESS, INT_ENABLE, 0x00)
    ## Disable FIFO
    bus.write_byte_data(MPU9250_ADDRESS, FIFO_EN, 0x00)
    ## Turn on internal clock source
    bus.write_byte_data(MPU9250_ADDRESS, PWR_MGMT_1, 0x00)
    ## Disable I2C master
    bus.write_byte_data(MPU9250_ADDRESS, I2C_MST_CTRL, 0x00)
    ## Disable FIFO and I2C master modes
    bus.write_byte_data(MPU9250_ADDRESS, USER_CTRL, 0x00)
    ## Reset FIFO and DMP
    bus.write_byte_data(MPU9250_ADDRESS, USER_CTRL, 0x0C)
    time.sleep(0.015)

    ## Configure MPU6050 gyro and accelerometer for bias calculation
    ## Set low-pass filter to 188 Hz
    bus.write_byte_data(MPU9250_ADDRESS, CONFIG, 0x01)
    ## Set sample rate to 1 kHz
    bus.write_byte_data(MPU9250_ADDRESS, SMPLRT_DIV, 0x00)
    ## Set gyro full-scale to 250 degrees per second, maximum sensitivity
    bus.write_byte_data(MPU9250_ADDRESS, GYRO_CONFIG, 0x00)
    ## Set accelerometer full-scale to 2 g, maximum sensitivity
    bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG, 0x00)

    ## Configure FIFO to capture accelerometer and gyro data for bias calculation
    bus.write_byte_data(MPU9250_ADDRESS, USER_CTRL, 0x40)  # Enable FIFO
    ## Enable gyro and accelerometer sensors for FIFO  (max size 512 bytes in MPU-9150)
    bus.write_byte_data(MPU9250_ADDRESS, FIFO_EN, 0x78)
    time.sleep(0.04)  # accumulate 40 samples in 40 milliseconds = 480 bytes

    ## At end of sample accumulation, turn off FIFO sensor read
    ## Disable gyro and accelerometer sensors for FIFO
    bus.write_byte_data(MPU9250_ADDRESS, FIFO_EN, 0x00)
    ## Read FIFO sample count
    data = bus.read_i2c_block_data(MPU9250_ADDRESS, FIFO_COUNTH, 2)
    fifo_count = (data[0] << 8) | data[1]
    ## How many sets of full gyro and accelerometer data for averaging
    packet_count = int(fifo_count / 12)

    accel_temp = [0, 0, 0]
    gyro_temp = [0, 0, 0]
    for ii in range(packet_count):
        ## Read data for averaging
        data = bus.read_i2c_block_data(MPU9250_ADDRESS, FIFO_R_W, 12)
        ## Form signed 16-bit integer for each sample in FIFO
        accel_temp[0] = uint_16_to_int16((data[0] << 8) | data[1])
        accel_temp[1] = uint_16_to_int16((data[2] << 8) | data[3])
        accel_temp[2] = uint_16_to_int16((data[4] << 8) | data[5])
        gyro_temp[0]  = uint_16_to_int16((data[6] << 8) | data[7])
        gyro_temp[1]  = uint_16_to_int16((data[8] << 8) | data[9])
        gyro_temp[2]  = uint_16_to_int16((data[10] << 8) | data[11])

        ## Sum individual signed 16-bit biases to get accumulated signed 32-bit biases.
        accel_bias[0] += accel_temp[0]
        accel_bias[1] += accel_temp[1]
        accel_bias[2] += accel_temp[2]
        gyro_bias[0]  += gyro_temp[0]
        gyro_bias[1]  += gyro_temp[1]
        gyro_bias[2]  += gyro_temp[2]

    ## Sum individual signed 16-bit biases to get accumulated signed 32-bit biases
    accel_bias[0] /= packet_count
    accel_bias[1] /= packet_count
    accel_bias[2] /= packet_count
    gyro_bias[0]  /= packet_count
    gyro_bias[1]  /= packet_count
    gyro_bias[2]  /= packet_count

    ## Sum individual signed 16-bit biases to get accumulated signed 32-bit biases
    if (accel_bias[2] > 0):
        accel_bias[2] -= accelsensitivity
    else:
        accel_bias[2] += accelsensitivity;

    ## Construct the gyro biases for push to the hardware gyro bias registers,
    ## which are reset to zero upon device startup.
    ## Divide by 4 to get 32.9 LSB per deg/s to conform to expected bias input
    ## format.
    data[0] = (-int(gyro_bias[0]/4)  >> 8) & 0xFF # Biases are additive, so change sign on calculated average gyro biases
    data[1] = (-int(gyro_bias[0]/4))       & 0xFF
    data[2] = (-int(gyro_bias[1]/4)  >> 8) & 0xFF
    data[3] = (-int(gyro_bias[1]/4))       & 0xFF
    data[4] = (-int(gyro_bias[2]/4)  >> 8) & 0xFF
    data[5] = (-int(gyro_bias[2]/4))       & 0xFF

    ## Push gyro biases to hardware registers
    bus.write_byte_data(MPU9250_ADDRESS, XG_OFFSET_H, data[0])
    bus.write_byte_data(MPU9250_ADDRESS, XG_OFFSET_L, data[1])
    bus.write_byte_data(MPU9250_ADDRESS, YG_OFFSET_H, data[2])
    bus.write_byte_data(MPU9250_ADDRESS, YG_OFFSET_L, data[3])
    bus.write_byte_data(MPU9250_ADDRESS, ZG_OFFSET_H, data[4])
    bus.write_byte_data(MPU9250_ADDRESS, ZG_OFFSET_L, data[5])

    ## Output scaled gyro biases for display in the main program
    gyroBias[0] = gyro_bias[0] / gyrosensitivity
    gyroBias[1] = gyro_bias[1] / gyrosensitivity
    gyroBias[2] = gyro_bias[2] / gyrosensitivity

    ## Construct the accelerometer biases for push to the hardware accelerometer
    ## bias registers. These registers contain factory trim values which must be
    ## added to the calculated accelerometer biases; on boot up these registers
    ## will hold non-zero values. In addition, bit 0 of the lower byte must be
    ## preserved since it is used for temperature compensation calculations.
    ## Accelerometer bias registers expect bias input as 2048 LSB per g, so that
    ## the accelerometer biases calculated above must be divided by 8.

    ## A place to hold the factory accelerometer trim biases
    accel_bias_reg = [0, 0, 0]
    ## Read factory accelerometer trim values
    data = bus.read_i2c_block_data(MPU9250_ADDRESS, XA_OFFSET_H, 2)
    accel_bias_reg[0] = (data[0] << 8) | data[1]
    data = bus.read_i2c_block_data(MPU9250_ADDRESS, YA_OFFSET_H, 2)
    accel_bias_reg[1] = (data[0] << 8) | data[1]
    data = bus.read_i2c_block_data(MPU9250_ADDRESS, ZA_OFFSET_H, 2)
    accel_bias_reg[2] = (data[0] << 8) | data[1]

    ## Define mask for temperature compensation bit 0 of lower byte of
    ## accelerometer bias registers
    mask = 1
    ## Define array to hold mask bit for each accelerometer bias axis
    mask_bit = [0, 0, 0]

    for ii in range(3):
        ## If temperature compensation bit is set, record that fact in mask_bit
        if (accel_bias_reg[ii] & mask):
            mask_bit[ii] = 0x01

    ## Construct total accelerometer bias, including calculated average
    ## accelerometer bias from above
    ## Subtract calculated averaged accelerometer bias scaled to 2048 LSB/g
    ## (16 g full scale)
    accel_bias_reg[0] -= accel_bias[0] / 8
    accel_bias_reg[1] -= accel_bias[1] / 8
    accel_bias_reg[2] -= accel_bias[2] / 8

    accel_bias_reg[0] = int(accel_bias_reg[0])
    accel_bias_reg[1] = int(accel_bias_reg[1])
    accel_bias_reg[2] = int(accel_bias_reg[2])

    data = [0, 0, 0, 0, 0, 0]

    data[0] = (accel_bias_reg[0] >> 8) & 0xFF
    data[1] = (accel_bias_reg[0])      & 0xFF
    ## preserve temperature compensation bit when writing back to accelerometer
    ## bias registers
    data[1] = data[1] | mask_bit[0]
    data[2] = (accel_bias_reg[1] >> 8) & 0xFF
    data[3] = (accel_bias_reg[1])      & 0xFF
    ## Preserve temperature compensation bit when writing back to accelerometer
    ## bias registers
    data[3] = data[3] | mask_bit[1]
    data[4] = (accel_bias_reg[2] >> 8) & 0xFF
    data[5] = (accel_bias_reg[2])      & 0xFF
    ## Preserve temperature compensation bit when writing back to accelerometer
    ## bias registers
    data[5] = data[5] | mask_bit[2];

    ## Apparently this is not working for the acceleration biases in the MPU-9250
    ## Are we handling the temperature correction bit properly?
    ## Push accelerometer biases to hardware registers
    bus.write_byte_data(MPU9250_ADDRESS, XA_OFFSET_H, data[0])
    bus.write_byte_data(MPU9250_ADDRESS, XA_OFFSET_L, data[1])
    bus.write_byte_data(MPU9250_ADDRESS, YA_OFFSET_H, data[2])
    bus.write_byte_data(MPU9250_ADDRESS, YA_OFFSET_L, data[3])
    bus.write_byte_data(MPU9250_ADDRESS, ZA_OFFSET_H, data[4])
    bus.write_byte_data(MPU9250_ADDRESS, ZA_OFFSET_L, data[5])

    ## Output scaled accelerometer biases for display in the main program
    accelBias[0] = accel_bias[0] / accelsensitivity
    accelBias[1] = accel_bias[1] / accelsensitivity
    accelBias[2] = accel_bias[2] / accelsensitivity

    return gyroBias, accelBias

def initMPU9250():
    ## wake up device
    ## Clear sleep mode bit (6), enable all sensors
    bus.write_byte_data(MPU9250_ADDRESS, PWR_MGMT_1, 0x00)
    time.sleep(0.1) ## Wait for all registers to reset

    ## Get stable time source
    ## Auto select clock source to be PLL gyroscope reference if ready else
    bus.write_byte_data(MPU9250_ADDRESS, PWR_MGMT_1, 0x01)
    time.sleep(0.2)

    ## Configure Gyro and Thermometer
    ## Disable FSYNC and set thermometer and gyro bandwidth to 41 and 42 Hz,
    ## respectively;
    ## minimum delay time for this setting is 5.9 ms, which means sensor fusion
    ## update rates cannot be higher than 1 / 0.0059 = 170 Hz
    ## DLPF_CFG = bits 2:0 = 011; this limits the sample rate to 1000 Hz for both
    ## With the MPU9250, it is possible to get gyro sample rates of 32 kHz (!),
    ## 8 kHz, or 1 kHz
    bus.write_byte_data(MPU9250_ADDRESS, CONFIG, 0x03)

    ## Set sample rate = gyroscope output rate/(1 + SMPLRT_DIV)
    ## Use a 200 Hz rate; a rate consistent with the filter update rate
    ## determined inset in CONFIG above.
    bus.write_byte_data(MPU9250_ADDRESS, SMPLRT_DIV, 0x04)

    ## Set gyroscope full scale range
    ## Range selects FS_SEL and AFS_SEL are 0 - 3, so 2-bit values are
    ## left-shifted into positions 4:3
    ## get current GYRO_CONFIG register value
    c = bus.read_byte_data(MPU9250_ADDRESS, GYRO_CONFIG)
    ## c = c & ~0xE0 # Clear self-test bits [7:5]
    c = c & ~0x02 # Clear Fchoice bits [1:0]
    c = c & ~0x18 # Clear AFS bits [4:3]
    c = c | Gscale << 3 # Set full scale range for the gyro
    ## Set Fchoice for the gyro to 11 by writing its inverse to bits 1:0 of
    ## GYRO_CONFIG
    ## c =| 0x00
    ## Write new GYRO_CONFIG value to register
    bus.write_byte_data(MPU9250_ADDRESS, GYRO_CONFIG, c)

    ## Set accelerometer full-scale range configuration
    ## Get current ACCEL_CONFIG register value
    c = bus.read_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG)
    ## c = c & ~0xE0 # Clear self-test bits [7:5]
    c = c & ~0x18 # Clear AFS bits [4:3]
    c = c | Ascale << 3 # Set full scale range for the accelerometer
    ## Write new ACCEL_CONFIG register value
    bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG, c)

    ## Set accelerometer sample rate configuration
    ## It is possible to get a 4 kHz sample rate from the accelerometer by
    ## choosing 1 for accel_fchoice_b bit [3]; in this case the bandwidth is
    ## 1.13 kHz
    ## Get current ACCEL_CONFIG2 register value
    c = bus.read_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG2)
    c = c & ~0x0F # Clear accel_fchoice_b (bit 3) and A_DLPFG (bits [2:0])
    c = c | 0x03  # Set accelerometer rate to 1 kHz and bandwidth to 41 Hz
    ## Write new ACCEL_CONFIG2 register value
    bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG2, c)
    ## The accelerometer, gyro, and thermometer are set to 1 kHz sample rates,
    ## but all these rates are further reduced by a factor of 5 to 200 Hz because
    ## of the SMPLRT_DIV setting

    ## Configure Interrupts and Bypass Enable
    ## Set interrupt pin active high, push-pull, hold interrupt pin level HIGH
    ## until interrupt cleared, clear on read of INT_STATUS, and enable
    ## I2C_BYPASS_EN so additional chips can join the I2C bus and all can be
    ## controlled by the Arduino as master.
    bus.write_byte_data(MPU9250_ADDRESS, INT_PIN_CFG, 0x22)
    ## Enable data ready (bit 0) interrupt
    bus.write_byte_data(MPU9250_ADDRESS, INT_ENABLE, 0x01)
    time.sleep(0.1)

def initAK8963():
    global bus
    destination = [0, 0, 0]
    
    ## First extract the factory calibration for each magnetometer axis
    ## TODO: Test this!! Likely doesn't work

    ## Disable master mode and clear all signal paths
    bus.write_byte_data(MPU9250_ADDRESS, 0x6A, 0x00) # Pass-Through Mode: The MPU-9250 directly connects the primary and auxiliary I2C buses together, allowing the system processor to directly communicate with any external sensors.
    time.sleep(0.01)
    bus.write_byte_data(MPU9250_ADDRESS, INT_PIN_CFG, 0x02)
    time.sleep(0.01)
    ##writeByte(MPU9250_ADDRESS, INT_ENABLE, 0x01)
    ##time.sleep(0.01)

    ## Power down magnetometer
    bus.write_byte_data(AK8963_ADDRESS, AK8963_CNTL, 0x00)
    time.sleep(0.01)
    
    ## Enter Fuse ROM access mode
    bus.write_byte_data(AK8963_ADDRESS, AK8963_CNTL, 0x0F)
    time.sleep(0.01)

    ## Read the x-, y-, and z-axis calibration values
    rawData = bus.read_i2c_block_data(AK8963_ADDRESS, AK8963_ASAX, 3)

    ## Return x-axis sensitivity adjustment values, etc.
    destination[0] =  rawData[0]
    destination[1] =  rawData[1]
    destination[2] =  rawData[2]

    ## Power down magnetometer
    bus.write_byte_data(AK8963_ADDRESS, AK8963_CNTL, 0x00)
    time.sleep(0.01)

    ## Configure the magnetometer for continuous read and highest resolution.
    ## Set Mscale bit 4 to 1 (0) to enable 16 (14) bit resolution in CNTL
    ## register, and enable continuous mode data acquisition Mmode (bits [3:0]),
    ## 0010 for 8 Hz and 0110 for 100 Hz sample rates.

    ## Set magnetometer data resolution and sample ODR
    bus.write_byte_data(AK8963_ADDRESS, AK8963_CNTL, Mscale << 4 | Mmode)
    time.sleep(0.01)

    return destination

def getAres():
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

def getGres():
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

def getMres() :
    ## Possible magnetometer scales (and their register bit settings) are:
    ## 14 bit resolution (0) and 16 bit resolution (1)
    if Mscale == MFS_14BITS:
        mRes = 10.0 * 4912.0 / 8190.0 # Proper scale to return milliGauss
    if Mscale == MFS_16BITS:
        mRes = 10.0 * 4912.0 / 32760.0 # Proper scale to return milliGauss

    return mRes

def readAccelData():
    destination = [0, 0, 0]
    
    ## Read the six raw data registers sequentially into data array
    rawData = bus.read_i2c_block_data(MPU9250_ADDRESS, ACCEL_XOUT_H, 6)

    ## Turn the MSB and LSB into a signed 16-bit value
    destination[0] = uint_16_to_int16((rawData[0] << 8) | rawData[1])
    destination[1] = uint_16_to_int16((rawData[2] << 8) | rawData[3])
    destination[2] = uint_16_to_int16((rawData[4] << 8) | rawData[5])
    
    return destination

def readGyroData():
    destination = [0, 0, 0]
    
    ## Read the six raw data registers sequentially into data array
    rawData = bus.read_i2c_block_data(MPU9250_ADDRESS, GYRO_XOUT_H, 6)

    ## Turn the MSB and LSB into a signed 16-bit value
    destination[0] = uint_16_to_int16((rawData[0] << 8) | rawData[1])
    destination[1] = uint_16_to_int16((rawData[2] << 8) | rawData[3])
    destination[2] = uint_16_to_int16((rawData[4] << 8) | rawData[5])

    return destination

def readMagData():
    ## x/y/z gyro register data, ST2 register stored here, must read ST2 at end
    ## of data acquisition
    
    destination = [0, 0, 0]

    ## Wait for magnetometer data ready bit to be set
    if (bus.read_byte_data(AK8963_ADDRESS, AK8963_ST1) & 0x01):
        ## Read the six raw data and ST2 registers sequentially into data array
        rawData = bus.read_i2c_block_data(AK8963_ADDRESS, AK8963_XOUT_L, 7)
        c = rawData[6] # End data read by reading ST2 register
        ## Check if magnetic sensor overflow set, if not then report data
        if (not(c & 0x08)):
            ## Turn the MSB and LSB into a signed 16-bit value
            ## Data stored as little Endian
            destination[0] = uint_16_to_int16((rawData[1] << 8) | rawData[0])
            destination[1] = uint_16_to_int16((rawData[3] << 8) | rawData[2])
            destination[2] = uint_16_to_int16((rawData[5] << 8) | rawData[4])
    
    return destination

def setup():
    global bus
    global factoryMagCalibration
    
    bus = smbus.SMBus(1)

    ## Read the WHO_AM_I register, this is a good test of communication
    c = bus.read_byte_data(MPU9250_ADDRESS, WHO_AM_I_MPU9250)
    print("MPU9250 I AM", hex(c), "and I should be 0x71")
    if (c != 0x71): # MPU9250 WHO_AM_I should always be 0x71
        ## Communication with MPU9250 failed, stop here
        print("Communication with 9250 failed, abort!")
        ### ABORT !!!!! ###
    else:
        print("MPU9250 is online...")

    ## Start by performing self test and reporting values
    selfTest = MPU9250SelfTest()
    print("x-axis self test: acceleration trim within", selfTest[0], "% of factory value")
    print("y-axis self test: acceleration trim within", selfTest[1], "% of factory value")
    print("z-axis self test: acceleration trim within", selfTest[2], "% of factory value")
    print("x-axis self test: gyration trim within", selfTest[3], "% of factory value")
    print("y-axis self test: gyration trim within", selfTest[4], "% of factory value")
    print("z-axis self test: gyration trim within", selfTest[5], "% of factory value")

    ## Calibrate gyro and accelerometers, load biases in bias registers
    print("MPU9250 calibration. Don't move it for 8 seconds")
    time.sleep(4)
    gyroBias, accelBias = calibrateMPU9250()
    print("Done!")
    print("MPU9250 bias")
    print("  acceleration (x, y, z):", accelBias[0], ", ", accelBias[1], ", ", accelBias[2], "g")
    print("  gyration (x, y, z):", gyroBias[0], ", ", gyroBias[1], ", ", gyroBias[2], "deg/s")

    ## Initialize device for active mode read of acclerometer, gyroscope, and temperature
    initMPU9250()
    print("MPU9250 initialized for active data mode...")

    ## Read the WHO_AM_I register of the magnetometer, this is a good test of communication
    d = bus.read_byte_data(AK8963_ADDRESS, WHO_AM_I_AK8963)
    print("AK8963 I AM", hex(d), "and I should be 0x48")
    if (d != 0x48): # AK8963 WHO_AM_I should always be 0x48
        ## Communication with MPU9250 failed, stop here
        print("Communication with AK8963 failed, abort!")
        ### ABORT !!!!! ###
    else:
        print("AK8963 is online...")

    ## Initialize device for active mode read of magnetometer
    ## and Get magnetometer calibration from AK8963 ROM
    factoryMagCalibration = initAK8963()
    print("Magnetometer calibration values: ")
    print("  X-Axis factory sensitivity adjustment value:", (factoryMagCalibration[0] - 128)/256. + 1.)
    print("  Y-Axis factory sensitivity adjustment value:", (factoryMagCalibration[1] - 128)/256. + 1.)
    print("  Z-Axis factory sensitivity adjustment value:", (factoryMagCalibration[2] - 128)/256. + 1.)
    print("AK8963 initialized for active data mode...")


    ## Get sensor resolutions, only need to do this once
    aRes = getAres()
    gRes = getGres()
    mRes = getMres()
    print("Sensors resolutions:");
    print("  Acceleration:", aRes,"g per LSB")
    print("  Gyration:", gRes, "DPS per LSB")
    print("  Magnetic field:", mRes, "mG per LSB")

def main():
    global running
    global factoryMagCalibration
    
    setup()

    connected = False
    while not(connected):
        try:
            server_socket = socket.socket()
            server_socket.bind(('192.168.0.43', 50000))
            server_socket.listen(0)
            print('waiting a client ...')
            connection, address_ip = server_socket.accept()
            print('client accepted')
            stream = connection.makefile('wb')
            connected = True
        except:
            print("can't create a connection")

    keyboard.add_hotkey('d', stop_running)
    running = True
    last_t = 0
    t0 = time.perf_counter()
    while running:
        if (bus.read_byte_data(MPU9250_ADDRESS, INT_STATUS) & 0x01):
            accelCount = readAccelData() # Read the x/y/z adc values
            gyroCount = readGyroData() # Read the x/y/z adc values
            magCount = readMagData() # Read the x/y/z adc values

            t = (time.perf_counter() - t0)*1000000 # compute time in microseconds
            delta_t = t - last_t # compute time variation
            last_t = t
            
            ## Build a log string
            imuLog = "" # Create a fresh line to log
            imuLog += str(int(t)) + ", " # Add time to log string
            imuLog += str(int(delta_t)) + ", "
            imuLog += str(accelCount[0]) + ", " # Add acceleration data to log string
            imuLog += str(accelCount[1]) + ", "
            imuLog += str(accelCount[2]) + ", "
            imuLog += str(gyroCount[0]) + ", " # Add gyrometer data to log string
            imuLog += str(gyroCount[1]) + ", "
            imuLog += str(gyroCount[2]) + ", "
            imuLog += str(magCount[0]) + ", " # Add magnetometer data to log string
            imuLog += str(magCount[1]) + ", "
            imuLog += str(magCount[2]) + ", "
            imuLog += str(factoryMagCalibration[0]) + ", " # Add factory magnetometer calibration data to log string
            imuLog += str(factoryMagCalibration[1]) + ", "
            imuLog += str(factoryMagCalibration[2]) + ", "
            imuLog += str(Ascale) + ", " # Add configuration informations to log string
            imuLog += str(Gscale) + ", "
            imuLog += str(Mscale) + ", "
            imuLog += str(Mmode) + ", "
            imuLog = imuLog[:(len(imuLog)-2)] # Remove last comma/space
            imuLog += "\n"; # Add a new line

            try:
                stream.write(imuLog.encode('Utf8'))
                stream.flush()
            except:
        ##        print("can't send data")
                pass

    try:
        stream.close()
        print('stream is closed')
    except:
        print("can't close stream")
    try:
        connection.close()
        print('connection socket is closed')
    except:
        print("can't close connection")
    try:
        server_socket.close()
        print('server socket is closed')
    except:
        print("can't close server socket")

    print('End of program')

if __name__ == '__main__':
    main()

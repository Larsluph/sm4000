#!/usr/bin/env python
# -*- coding: utf-8 -*-

##This code is writen from SparkFunBME280.h and SparkFunBME280.cpp
##BME280 Arduino and Teensy Driver
##Marshall Taylor @ SparkFun Electronics
##May 20, 2015
##https://github.com/sparkfun/BME280_Breakout
##The original code is released under the [MIT License](http://opensource.org/licenses/MIT).
##Please review the LICENSE.md file included with this example. If you have any questions 
##or concerns with licensing, please contact techsupport@sparkfun.com.
##Distributed as-is; no warranty is given.

##Adapted for python with Raspberry Pi by Stéphane Ramstein


import smbus
import time
import keyboard

MODE_SLEEP  = 0b00
MODE_FORCED = 0b01
MODE_NORMAL = 0b11

## Register names:
BME280_DIG_T1_LSB_REG			= 0x88
BME280_DIG_T1_MSB_REG			= 0x89
BME280_DIG_T2_LSB_REG			= 0x8A
BME280_DIG_T2_MSB_REG			= 0x8B
BME280_DIG_T3_LSB_REG			= 0x8C
BME280_DIG_T3_MSB_REG			= 0x8D
BME280_DIG_P1_LSB_REG			= 0x8E
BME280_DIG_P1_MSB_REG			= 0x8F
BME280_DIG_P2_LSB_REG			= 0x90
BME280_DIG_P2_MSB_REG			= 0x91
BME280_DIG_P3_LSB_REG			= 0x92
BME280_DIG_P3_MSB_REG			= 0x93
BME280_DIG_P4_LSB_REG			= 0x94
BME280_DIG_P4_MSB_REG			= 0x95
BME280_DIG_P5_LSB_REG			= 0x96
BME280_DIG_P5_MSB_REG			= 0x97
BME280_DIG_P6_LSB_REG			= 0x98
BME280_DIG_P6_MSB_REG			= 0x99
BME280_DIG_P7_LSB_REG			= 0x9A
BME280_DIG_P7_MSB_REG			= 0x9B
BME280_DIG_P8_LSB_REG			= 0x9C
BME280_DIG_P8_MSB_REG			= 0x9D
BME280_DIG_P9_LSB_REG			= 0x9E
BME280_DIG_P9_MSB_REG			= 0x9F
BME280_DIG_H1_REG		        = 0xA1
BME280_CHIP_ID_REG			= 0xD0 # Chip ID
BME280_RST_REG				= 0xE0 # Softreset Reg
BME280_DIG_H2_LSB_REG			= 0xE1
BME280_DIG_H2_MSB_REG			= 0xE2
BME280_DIG_H3_REG			= 0xE3
BME280_DIG_H4_MSB_REG			= 0xE4
BME280_DIG_H4_LSB_REG			= 0xE5
BME280_DIG_H5_MSB_REG			= 0xE6
BME280_DIG_H6_REG			= 0xE7
BME280_CTRL_HUMIDITY_REG		= 0xF2 # Ctrl Humidity Reg
BME280_STAT_REG				= 0xF3 # Status Reg
BME280_CTRL_MEAS_REG			= 0xF4 # Ctrl Measure Reg
BME280_CONFIG_REG			= 0xF5 # Configuration Reg
BME280_PRESSURE_MSB_REG			= 0xF7 # Pressure MSB
BME280_PRESSURE_LSB_REG			= 0xF8 # Pressure LSB
BME280_PRESSURE_XLSB_REG		= 0xF9 # Pressure XLSB
BME280_TEMPERATURE_MSB_REG		= 0xFA # Temperature MSB
BME280_TEMPERATURE_LSB_REG		= 0xFB # Temperature LSB
BME280_TEMPERATURE_XLSB_REG		= 0xFC # Temperature XLSB
BME280_HUMIDITY_MSB_REG			= 0xFD # Humidity MSB
BME280_HUMIDITY_LSB_REG			= 0xFE # Humidity LSB

BME280_ADDRESS = 0x77

## These are deprecated settings
settings_runMode = 3   # Normal/Run
settings_tStandby = 0  # 0.5ms
settings_filter = 0    # Filter off
settings_tempOverSample = 1
settings_pressOverSample = 1
settings_humidOverSample = 1

referencePressure = 101325 # default reference pressure in Pa

def uint_8_to_int8(val): # convert unsigned 8 bit integers into signed ones.
    if (val >= 0x80):
        return -((0xFF - val) + 1)
    else:
        return val

def uint_16_to_int16(val): # convert unsigned 16 bit integers into signed ones.
    if (val >= 0x8000):
        return -((0xFFFF - val) + 1)
    else:
        return val

def setStandbyTime(timeSetting):
    ## Set the standby bits in the config register
    ## tStandby can be:
    ##   0, 0.5ms
    ##   1, 62.5ms
    ##   2, 125ms
    ##   3, 250ms
    ##   4, 500ms
    ##   5, 1000ms
    ##   6, 10ms
    ##   7, 20ms

    if (timeSetting > 0b111):
        timeSetting = 0 # Error check. Default to 0.5ms
    
    controlData = bus.read_byte_data(BME280_ADDRESS, BME280_CONFIG_REG)
    controlData &= ~( (1<<7) | (1<<6) | (1<<5) ) # Clear the 7/6/5 bits
    controlData |= (timeSetting << 5) # Align with bits 7/6/5
    bus.write_byte_data(BME280_ADDRESS, BME280_CONFIG_REG, controlData)

def setFilter(filterSetting):
    ## Set the filter bits in the config register
    ## filter can be off or number of FIR coefficients to use:
    ##   0, filter off
    ##   1, coefficients = 2
    ##   2, coefficients = 4
    ##   3, coefficients = 8
    ##   4, coefficients = 16
    
    if (filterSetting > 0b111):
        filterSetting = 0 # Error check. Default to filter off
    
    controlData = bus.read_byte_data(BME280_ADDRESS, BME280_CONFIG_REG)
    controlData &= ~( (1<<4) | (1<<3) | (1<<2) ) # Clear the 4/3/2 bits
    controlData |= (filterSetting << 2) # Align with bits 4/3/2
    bus.write_byte_data(BME280_ADDRESS, BME280_CONFIG_REG, controlData)

def setPressureOverSample(overSampleAmount):
    ## Set the pressure oversample value
    ## 0 turns off pressure sensing
    ## 1 to 16 are valid over sampling values
    
    overSampleAmount = checkSampleValue(overSampleAmount) # Error check
    
    originalMode = getMode() # Get the current mode so we can go back to it at the end

    setMode(MODE_SLEEP) # Config will only be writeable in sleep mode, so first go to sleep mode

    ## Set the osrs_p bits (4, 3, 2) to overSampleAmount
    controlData = bus.read_byte_data(BME280_ADDRESS, BME280_CTRL_MEAS_REG)
    controlData &= ~( (1<<4) | (1<<3) | (1<<2) ) # Clear bits 432
    controlData |= overSampleAmount << 2 # Align overSampleAmount to bits 4/3/2
    bus.write_byte_data(BME280_ADDRESS, BME280_CTRL_MEAS_REG, controlData)
    
    setMode(originalMode) # Return to the original user's choice

def setHumidityOverSample(overSampleAmount):
## Set the humidity oversample value
## 0 turns off humidity sensing
## 1 to 16 are valid over sampling values

    overSampleAmount = checkSampleValue(overSampleAmount) # Error check
    
    originalMode = getMode() # Get the current mode so we can go back to it at the end
    
    setMode(MODE_SLEEP) # Config will only be writeable in sleep mode, so first go to sleep mode

    ## Set the osrs_h bits (2, 1, 0) to overSampleAmount
    controlData = bus.read_byte_data(BME280_ADDRESS, BME280_CTRL_HUMIDITY_REG)
    controlData &= ~( (1<<2) | (1<<1) | (1<<0) ) # Clear bits 2/1/0
    controlData |= overSampleAmount << 0 # Align overSampleAmount to bits 2/1/0
    bus.write_byte_data(BME280_ADDRESS, BME280_CTRL_HUMIDITY_REG, controlData)

    setMode(originalMode) # Return to the original user's choice

def setTempOverSample(overSampleAmount):
    ## Set the temperature oversample value
    ## 0 turns off temp sensing
    ## 1 to 16 are valid over sampling values

    overSampleAmount = checkSampleValue(overSampleAmount) # Error check
    
    originalMode = getMode() # Get the current mode so we can go back to it at the end
    
    setMode(MODE_SLEEP) # Config will only be writeable in sleep mode, so first go to sleep mode

    ## Set the osrs_t bits (7, 6, 5) to overSampleAmount
    controlData = bus.read_byte_data(BME280_ADDRESS, BME280_CTRL_MEAS_REG);
    controlData &= ~( (1<<7) | (1<<6) | (1<<5) ) # Clear bits 765
    controlData |= overSampleAmount << 5 # Align overSampleAmount to bits 7/6/5
    bus.write_byte_data(BME280_ADDRESS, BME280_CTRL_MEAS_REG, controlData)
    
    setMode(originalMode) # Return to the original user's choice

def checkSampleValue(userValue):
    ## Validates an over sample value
    ## Allowed values are 0 to 16
    ## These are used in the humidty, pressure, and temp oversample functions

    if userValue == 0:
        return 0
    elif userValue == 1:
        return 1
    elif userValue == 2:
        return 2
    elif userValue == 4:
        return 3
    elif userValue == 8:
        return 4
    elif userValue == 16:
        return 5
    else:
        return 1 # Default to 1x

def getMode():
    ## Gets the current mode bits in the ctrl_meas register
    ## Mode 00 = Sleep
    ## 01 and 10 = Forced
    ## 11 = Normal mode

    controlData = bus.read_byte_data(BME280_ADDRESS, BME280_CTRL_MEAS_REG)
    
    return controlData & 0b00000011 # Clear bits 7 through 2

def setMode(mode):
    ## Set the mode bits in the ctrl_meas register
    ## Mode 00 = Sleep
    ## 01 and 10 = Forced
    ## 11 = Normal mode

    if (mode > 0b11):
        mode = 0 # Error check. Default to sleep mode
    
    controlData = bus.read_byte_data(BME280_ADDRESS, BME280_CTRL_MEAS_REG)
    controlData &= ~( (1<<1) | (1<<0) ) # Clear the mode[1:0] bits
    controlData |= mode # Set
    bus.write_byte_data(BME280_ADDRESS, BME280_CTRL_MEAS_REG, controlData)

def readTempC():
    ## Returns temperature in DegC, resolution is 0.01 DegC. Output value of “5123” equals 51.23 DegC.
    ## t_fine carries fine temperature as global value
    global t_fine

    ## get the reading (adc_T);
    buffer = bus.read_i2c_block_data(BME280_ADDRESS, BME280_TEMPERATURE_MSB_REG, 3)
    adc_T = (buffer[0] << 12) | (buffer[1] << 4) | ((buffer[2] >> 4) & 0x0F)

    ## By datasheet, calibrate
    var1 = ((((adc_T>>3) - (calibration_dig_T1<<1))) * (calibration_dig_T2)) >> 11
    var2 = (((((adc_T>>4) - (calibration_dig_T1)) * ((adc_T>>4) - (calibration_dig_T1))) >> 12) *
        (calibration_dig_T3)) >> 14
    t_fine = var1 + var2
    output = (t_fine * 5 + 128) >> 8
    output = output / 100

    return output

def readTempF():
    output = readTempC()
    output = (output * 9) / 5 + 32

    return output

def readFloatHumidity():
    ## Returns humidity in %RH as unsigned 32 bit integer in Q22. 10 format (22 integer and 10 fractional bits).
    ## Output value of “47445” represents 47445/1024 = 46. 333 %RH
    buffer = bus.read_i2c_block_data(BME280_ADDRESS, BME280_HUMIDITY_MSB_REG, 2)
    adc_H = (buffer[0] << 8) | buffer[1]

    var1 = t_fine - 76800
    var1 = ((( ((adc_H << 14) - ((calibration_dig_H4) << 20) - (calibration_dig_H5) * var1)
        + 16384) >> 15) * (((((((var1 * (calibration_dig_H6)) >> 10) * (((var1 * (calibration_dig_H3)) >> 11) + 32768)) >> 10) + 2097152) *
        calibration_dig_H2 + 8192) >> 14))
    var1 = (var1 - (((((var1 >> 15) * (var1 >> 15)) >> 7) * (calibration_dig_H1)) >> 4))
    if var1 > 419430400:
        var1 = 419430400
    
    return (var1>>12) / 1024.0

def readFloatPressure():
    ## Returns pressure in Pa as unsigned 32 bit integer in Q24.8 format (24 integer bits and 8 fractional bits).
    ## Output value of “24674867” represents 24674867/256 = 96386.2 Pa = 963.862 hPa

    buffer = bus.read_i2c_block_data(BME280_ADDRESS, BME280_PRESSURE_MSB_REG, 3)
    adc_P = (buffer[0] << 12) | (buffer[1] << 4) | ((buffer[2] >> 4) & 0x0F)

    var1 = (t_fine) - 128000
    var2 = var1 * var1 * calibration_dig_P6
    var2 = var2 + ((var1 * calibration_dig_P5)<<17)
    var2 = var2 + ((calibration_dig_P4)<<35)
    var1 = ((var1 * var1 * calibration_dig_P3)>>8) + ((var1 * calibration_dig_P2)<<12)
    var1 = ((((1)<<47)+var1))*(calibration_dig_P1)>>33
    if (var1 == 0):
        return 0 # avoid exception caused by division by zero

    p_acc = 1048576 - adc_P
    p_acc = int((((p_acc<<31) - var2)*3125)/var1)
    var1 = ((calibration_dig_P9) * (p_acc>>13) * (p_acc>>13)) >> 25
    var2 = ((calibration_dig_P8) * p_acc) >> 19
    p_acc = ((p_acc + var1 + var2) >> 8) + ((calibration_dig_P7)<<4)

    return p_acc / 256.0
    return None

def setReferencePressure(refPressure):
    ## Sets the internal variable referencePressure
    global referencePressure
    
    referencePressure = refPressure

def getReferencePressure():
    ## Return the local reference pressure
    
    return(referencePressure)

def readFloatAltitudeMeters():
    heightOutput = -45846.2*((readFloatPressure()/referencePressure)**0.190263 - 1)

    return heightOutput

def readFloatAltitudeFeet():
    heightOutput = readFloatAltitudeMeters() * 3.28084

    return heightOutput

##//Check the measuring bit and return true while device is taking measurement
##bool BME280::isMeasuring(void)
##{
##	uint8_t stat = readRegister(BME280_STAT_REG);
##	return(stat & (1<<3)); //If the measuring bit (3) is set, return true
##}
##
##//Strictly resets.  Run .begin() afterwards
##void BME280::reset( void )
##{
##	writeRegister(BME280_RST_REG, 0xB6);
##	
##}

def setup():
    global bus
    global calibration_dig_T1
    global calibration_dig_T2
    global calibration_dig_T3
    global calibration_dig_P1
    global calibration_dig_P2
    global calibration_dig_P3
    global calibration_dig_P4
    global calibration_dig_P5
    global calibration_dig_P6
    global calibration_dig_P7
    global calibration_dig_P8
    global calibration_dig_P9
    global calibration_dig_H1
    global calibration_dig_H2
    global calibration_dig_H3
    global calibration_dig_H4
    global calibration_dig_H5
    global calibration_dig_H6

    bus = smbus.SMBus(1)

    ## Read the WHO_AM_I register, this is a good test of communication
    c = bus.read_byte_data(BME280_ADDRESS, BME280_CHIP_ID_REG)
    print("BME280 I AM", hex(c), "and I should be 0x60")
    if (c != 0x60): # BME280 BME280_CHIP_ID_REG should always be 0x60
        ## Communication with BME failed, stop here
        print("Communication with BME280 failed, abort!")
        ### ABORT !!!!! ###
    else:
        print("BME280 is online...")

    ## Reading all compensation data, range 0x88:A1, 0xE1:E7
    calibration_dig_T1 = (bus.read_byte_data(BME280_ADDRESS, BME280_DIG_T1_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_T1_LSB_REG)
    calibration_dig_T2 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_T2_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_T2_LSB_REG))
    calibration_dig_T3 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_T3_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_T3_LSB_REG))

    calibration_dig_P1 = (bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P1_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P1_LSB_REG)
    calibration_dig_P2 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P2_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P2_LSB_REG))
    calibration_dig_P3 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P3_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P3_LSB_REG))
    calibration_dig_P4 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P4_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P4_LSB_REG))
    calibration_dig_P5 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P5_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P5_LSB_REG))
    calibration_dig_P6 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P6_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P6_LSB_REG))
    calibration_dig_P7 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P7_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P7_LSB_REG))
    calibration_dig_P8 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P8_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P8_LSB_REG))
    calibration_dig_P9 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P9_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_P9_LSB_REG))

    calibration_dig_H1 = bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H1_REG)
    calibration_dig_H2 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H2_MSB_REG) << 8) + bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H2_LSB_REG))
    calibration_dig_H3 = bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H3_REG)
    calibration_dig_H4 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H4_MSB_REG) << 4) + (bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H4_LSB_REG) & 0x0F))
    calibration_dig_H5 = uint_16_to_int16((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H5_MSB_REG) << 4) + ((bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H4_LSB_REG) >> 4) & 0x0F))
    calibration_dig_H6 = uint_8_to_int8(bus.read_byte_data(BME280_ADDRESS, BME280_DIG_H6_REG))

    ## Most of the time the sensor will be init with default values
    ## But in case user has old/deprecated code, use the settings.x values
    setStandbyTime(settings_tStandby)
    setFilter(settings_filter)
    setPressureOverSample(settings_pressOverSample) # Default of 1x oversample
    setHumidityOverSample(settings_humidOverSample) # Default of 1x oversample
    setTempOverSample(settings_tempOverSample) # Default of 1x oversample

    setMode(MODE_NORMAL) # Go!

def main():
    setup()

    print('Temperature:', readTempC(), '°C')
    print('Temperature:', readTempF(), '°F')
    print('Humidity:', readFloatHumidity(), '%')
    print('Pressure:', readFloatPressure(), 'Pa')

    setReferencePressure(readFloatPressure())
    print('Altitude:', readFloatAltitudeMeters(), 'm')
    print('Altitude:', readFloatAltitudeFeet(), 'feet')

##    setFilter(4)
##    setTempOverSample(5)
##    setPressureOverSample(5)

    setReferencePressure(readFloatPressure())

    for i in range(10):
        print('Pressure:', readFloatPressure(), 'Pa')
        print('Altitude:', readFloatAltitudeMeters(), 'm')
        time.sleep(0.01)
    
            
##            ## Build a log string
##            imuLog = "" # Create a fresh line to log
##            imuLog += str(int(t)) + ", " # Add time to log string
##            imuLog += str(int(delta_t)) + ", "
##            imuLog += str(tempCount) + ", " # Add temperature to log string
##            imuLog += str(accelCount[0]) + ", " # Add acceleration data to log string
##            imuLog += str(accelCount[1]) + ", "
##            imuLog += str(accelCount[2]) + ", "
##            imuLog += str(gyroCount[0]) + ", " # Add gyrometer data to log string
##            imuLog += str(gyroCount[1]) + ", "
##            imuLog += str(gyroCount[2]) + ", "
##            imuLog += str(magCount[0]) + ", " # Add magnetometer data to log string
##            imuLog += str(magCount[1]) + ", "
##            imuLog += str(magCount[2]) + ", "
##            imuLog += str(factoryMagCalibration[0]) + ", " # Add factory magnetometer calibration data to log string
##            imuLog += str(factoryMagCalibration[1]) + ", "
##            imuLog += str(factoryMagCalibration[2]) + ", "
##            imuLog += str(Ascale) + ", " # Add configuration informations to log string
##            imuLog += str(Gscale) + ", "
##            imuLog += str(Mscale) + ", "
##            imuLog += str(Mmode) + ", "
##            imuLog = imuLog[:(len(imuLog)-2)] # Remove last comma/space
##            imuLog += "\n"; # Add a new line
##
##            print(imuLog, end='')

if __name__ == '__main__':
    main()

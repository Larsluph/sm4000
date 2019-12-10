#!/usr/bin python3
#-*- coding:utf-8 -*-

import time

import adafruit_ads1x15.ads1115 as ADS
import board
import busio
import smbus
from adafruit_ads1x15.analog_in import AnalogIn

##################
## MAIN PROGRAM ##
##################

# setup ads
i2c = busio.I2C(board.SCL, board.SDA)
ads_water = ADS.ADS1115(i2c,address=0x48)
# ads_battery = ADS.ADS1115(i2c,address=0x49)


water_lvl = AnalogIn(ads_water, ADS.P3)

while True:
	print(ads_water.gain,water_lvl.value)
	time.sleep(.5)

raise SystemExit

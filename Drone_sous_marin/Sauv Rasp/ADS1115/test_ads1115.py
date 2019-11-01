#!/usr/bin/env python
# -*- coding: utf-8 -*-

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)

# create the ADC object
ads = ADS.ADS1115(i2c)

# create the analog input channel, providing the ADC object and the pin to which the signal is attached
chan = AnalogIn(ads, ADS.P0)

print("Gain:", ads.gain)
print("ADC value:", chan.value, "Voltage value:", chan.voltage)

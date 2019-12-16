#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import ms5837
import time

sensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)
#sensor = ms5837.MS5837_30BA(0) # Specify I2C bus
#sensor = ms5837.MS5837_02BA()
#sensor = ms5837.MS5837_02BA(0)
#sensor = ms5837.MS5837(model=ms5837.MS5837_MODEL_30BA, bus=0) # Specify model and bus

# We must initialize the sensor before reading it
if not sensor.init():
    print("Sensor could not be initialized")
    exit(1)

# We have to read values from sensor to update pressure and temperature
if not sensor.read():
    print("Sensor read failed!")
    exit(1)

print("Pressure:")
print(sensor.pressure(ms5837.UNITS_atm), "atm")
print(sensor.pressure(ms5837.UNITS_Torr), "Torr")
print(sensor.pressure(ms5837.UNITS_psi), "psi")

print("Temperature:")
print(sensor.temperature(ms5837.UNITS_Centigrade), "C")
print(sensor.temperature(ms5837.UNITS_Farenheit), "F")
print(sensor.temperature(ms5837.UNITS_Kelvin), "K")

freshwaterDepth = sensor.depth() # default is freshwater
sensor.setFluidDensity(ms5837.DENSITY_SALTWATER)
saltwaterDepth = sensor.depth() # No nead to read() again
sensor.setFluidDensity(1000) # kg/m^3
print("Depth:")
print(freshwaterDepth, "m (freshwater)")
print(saltwaterDepth, "m (saltwater)")

# fluidDensity doesn't matter for altitude() (always MSL air density)
print("MSL Relative Altitude:")
print(sensor.altitude(), "m") # relative to Mean Sea Level pressure in air

time.sleep(5)

# Spew readings
while True:
    if sensor.read():
        print("P:")
        print(sensor.pressure(), "mbar") # Default is mbar (no arguments)
        print(sensor.pressure(ms5837.UNITS_psi), "psi") # Request psi
        print(sensor.temperature(), "C") # Default is degrees C (no arguments)
        print(sensor.temperature(ms5837.UNITS_Farenheit), "F") # Request Farenheit
    else:
        print("Sensor read failed!")
        exit(1)

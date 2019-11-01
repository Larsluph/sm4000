#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import socket
##import keyboard

# ADS1115 imports
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio

# MS5837 imports
import ms5837

##def stop_running():
##    global running
##
##    running = False

def main():
    global running

    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    chan = AnalogIn(ads, ADS.P0)

    sensor = ms5837.MS5837_30BA()
    sensor.init()
    
    try:
        server_socket = socket.socket()
        server_socket.bind(('192.168.137.2', 50000))
        server_socket.listen(0)
        print('waiting a client ...')
        connection, address_ip = server_socket.accept()
        print('client accepted')
        stream = connection.makefile('wb')
    except:
        print("can't create a connection")

    t0 = time.perf_counter()
    t_last = 0
##    keyboard.add_hotkey('q', stop_running)
    i = 0
    running = True
    while running:
        ADC0_value = chan.value
        ADC0_voltage = chan.voltage
        sensor.read()
        pressure = sensor.pressure()
        temperature = sensor.temperature()
        freshwaterDepth = sensor.depth()
        t = (time.perf_counter() - t0) * 1000
        delta_t = t - t_last
        t_last = t
        data = str(temperature) + ',' + str(pressure) + ',' + str(freshwaterDepth) + ',' + str(ADC0_value) + ',' + str(ADC0_voltage) + '\n'
        i = i + 1
        try:
            stream.write(data.encode('Utf8'))
            stream.flush()
        except:
    ##        print("can't send data")
            pass
        time.sleep(1)


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

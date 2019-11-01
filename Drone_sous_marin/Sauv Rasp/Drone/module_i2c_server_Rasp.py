#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math, time, socket, keyboard, smbus # Module de prise en charge du bus i2C

# This is the address value read via the i2cdetect command
address = 0x68

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt(a**2+b**2)

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def stop_running():
    global running

    running = False

def main():
    global bus
    global running
    global ip
    
    bus = smbus.SMBus(1)

    # Now wake the 6050 up as it starts in sleep mode
    bus.write_byte_data(address, power_mgmt_1, 0)

    try:
        server_socket = socket.socket()
        server_socket.bind(('192.168.0.43', 50000))
        server_socket.listen(0)
        print('waiting a client ...')
        connection, address_ip = server_socket.accept()
        print('client accepted')
        stream = connection.makefile('wb')
    except:
        print("can't create a connection")


    t0 = time.perf_counter()
    t_last = 0
    keyboard.add_hotkey('p', stop_running)
    i = 0
    running = True
    while running:
        gyro_xout = read_word_2c(0x43)
        gyro_yout = read_word_2c(0x45)
        gyro_zout = read_word_2c(0x47)
        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)
        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0
        t = (time.perf_counter() - t0) * 1000
        delta_t = t - t_last
        t_last = t
        data = str(i) + ',' + str(t) + ',' + str(delta_t) + ',' + str(accel_xout_scaled) + ',' + str(accel_yout_scaled) + ',' + str(accel_zout_scaled) + '\n'
        i = i + 1
        try:
            stream.write(data.encode('Utf8'))
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

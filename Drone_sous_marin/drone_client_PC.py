#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import socket
# import module_commande_client_PC
# import module_i2c_client_PC
import module_MPU9250_client_PC
import MPU9250_openGL

def client_loop(module, address, port):
    connected = False
    while not(connected):
        try:
            client_socket = socket.socket()
            client_socket.connect((address, port))
            stream = client_socket.makefile('rb')
            print('connection with server established')
            connected = True
        except:
            print("can't established connection")

    print('waiting incoming data')

    running = True
    while running:
        try:
            data = stream.readline()
            data = data.decode('Utf8')
            data = data.split(',')

            if len(data) == 0:
                running = False
            else:
                module.process_data(data)

        except:
            print("can't read incoming data")
            running = False

    try:
        stream.close()
        print('stream closed')
    except:
        print("can't close stream")
    try:
        client_socket.close()
        print('client socket closed')
    except:
        print("can't close client socket")

def main():
    # module_commande = threading.Thread(None, module_commande_client_PC.main, None)
    # module_i2c = threading.Thread(None, module_i2c_client_PC.main, None)
    # module_MPU9250 = threading.Thread(None, module_MPU9250_client_PC.main, None)
    #
    # module_MPU9250.start()

    MPU9250_thread = threading.Thread(None, client_loop, None, (module_MPU9250_client_PC, '192.168.0.43', 50000))
    MPU9250_thread.start()

    openGL_thread = threading.Thread(None, MPU9250_openGL.main, None)
    openGL_thread.start()

    while True:
        data = module_MPU9250_client_PC.data_values

        if data != None:
            print(data[5])
            MPU9250_openGL.qw = data[5][0]
            MPU9250_openGL.qx = data[5][1]
            MPU9250_openGL.qy = data[5][2]
            MPU9250_openGL.qz = data[5][3]

if __name__ == '__main__':
    main()

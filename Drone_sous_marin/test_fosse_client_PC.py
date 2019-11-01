#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

def main():
    connected = False
    while not(connected):
        try:
            client_socket = socket.socket()
            client_socket.connect(('192.168.137.2', 50000))
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
                print(data)

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

if __name__ == '__main__':
    main()

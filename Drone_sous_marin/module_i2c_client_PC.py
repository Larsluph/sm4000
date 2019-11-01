#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time

def main():
    try:
        client_socket = socket.socket()
        client_socket.connect(('192.168.0.43', 50000))
        stream = client_socket.makefile('rb')
        print('connection with server established')
    except:
        print("can't established connection")

    print('reading incoming data')

    running = True
    while running:
        try:
            data = stream.readline()
            print(data.decode('Utf8'))
        except:
            print("can't read incoming data")
            running = False
        if len(data) < 10:
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

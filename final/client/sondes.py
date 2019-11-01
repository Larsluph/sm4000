#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, os

os.system("title client_sondes")

def main():
    connected = False
    while not(connected):
        try:
            print('Connecting...')
            ip = ('192.168.137.2', 50003)
            client_socket = socket.socket()
            client_socket.connect(ip)
            stream = client_socket.makefile('rb')
            print('connection with server established')
            connected = True
        except:
            print("can't established connection")

    print('waiting incoming data')

    running = True
    with open(time.strftime('C:\\sm4000_received_data\\probes_data_%d-%m-%Y_%H-%M-%S.txt'),mode='x') as output:
        while running:
            try:
                data = stream.readline()
                data = data.decode('Utf8')
                data = data.split(',')

                if len(data) == 0:
                    running = False
                else:
                    print(data)
                    print(data,file=output,flush=True)

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

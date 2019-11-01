#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import keyboard

def stop_running():
    global running

    running = False

def main():
    global running

    try:
        server_socket = socket.socket()
        server_socket.bind(('192.168.0.43', 50050))
        server_socket.listen(0)
        print('waiting a client ...')
        connection, address_ip = server_socket.accept()
        print('client accepted')
    except:
        print("can't create a connection")


    keyboard.add_hotkey('s', stop_running)
    i = 0
    running = True
    while running:
        try:
            incomming_data = connection.recv(1024) # Receive data from the socket. 1024 is the maximum amount of data to be received. Return a bytes object.
            print(incomming_data.decode('Utf8')) # The byte object must be decode into a string
        except:
    ##        print("can't send data")
            pass

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

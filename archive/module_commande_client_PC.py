#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import keyboard

def forward_key_pressed():
    global client_socket_1
    client_socket_1.send('forward'.encode('Utf8'))

def backward_key_pressed():
    global client_socket_1
    client_socket_1.send('backward'.encode('Utf8'))

def left_key_pressed():
    global client_socket_1
    client_socket_1.send('left'.encode('Utf8'))

def right_key_pressed():
    global client_socket_1
    client_socket_1.send('right'.encode('Utf8'))

def up_key_pressed():
    global client_socket_1
    client_socket_1.send('up'.encode('Utf8'))

def down_key_pressed():
    global client_socket_1
    client_socket_1.send('down'.encode('Utf8'))

def stop_key_pressed():
    global client_socket_1
    client_socket_1.send('stop'.encode('Utf8'))

def stop_running():
    global running

    running = False
    client_socket_1.send('quit'.encode('Utf8'))

def main():
    global running
    global client_socket_1

    client_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a new socket with the default address family and socket type

    print('client 1 connecting ...')
    client_socket_1.connect(('192.168.137.2', 50050)) # Connect to a remote server socket at address 192.168.0.16:50000
    print('client 1 connected')

    time.sleep(2)

    keyboard.add_hotkey('up', forward_key_pressed)
    keyboard.add_hotkey('down', backward_key_pressed)
    keyboard.add_hotkey('left', left_key_pressed)
    keyboard.add_hotkey('right', right_key_pressed)
    keyboard.add_hotkey('a', up_key_pressed)
    keyboard.add_hotkey('q', down_key_pressed)
    keyboard.add_hotkey('space', stop_key_pressed)
    keyboard.add_hotkey('p', stop_running)

    running = True
    while running:
        pass

    client_socket_1.close() # Close the socket
    print('client 1 closed')

if __name__ == '__main__':
    main()

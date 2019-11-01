#!usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, socket, time

os.system("clear")

# DONE : server set up
ip = '192.168.0.23'

server_socket = socket.socket()
server_socket.bind((ip,50000))
print("server binded to '%s:50000'" % (ip) )
print("Waiting for remote")
server_socket.listen(0)
telecommande, address1 = server_socket.accept()

print("Connected")

print("Waiting for instructions...")

cmd = [False,[0,0,0]]

while True:
	cmd = telecommande.recv(5000).decode('Utf8')
	print(cmd)
	print(len(cmd))
	time.sleep(0.1)
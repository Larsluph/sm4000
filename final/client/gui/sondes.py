#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard
import tkinter as tk

win = tk.Tk()
win.title("client_sondes GUI")

try:
    ip = ("192.168.137.2",50003)

    print("Connecting to %s..."%(":".join(map(str,ip))))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ip)
    print("Connected!")
except:
    print("unable to connect to host\nExiting...")
    time.sleep(1)
    raise SystemExit

try:
    os.system("mkdir sm4000_received_data\\probes_data")
except:
    pass

keyboard.add_hotkey('esc',lambda: exec("global running;running=False"),suppress=False)
print("waiting for data...")

tk_vars = {
    "status":tk.StringVar(),
    "i":tk.StringVar(),
    "t":tk.StringVar(),
    "delta_t":tk.StringVar(),
    "lvl_val":tk.StringVar(),
    "lvl_volt":tk.StringVar(),
    "bat_val":tk.StringVar(),
    "bat_volt":tk.StringVar(),
    "pressure":tk.StringVar(),
    "temp":tk.StringVar(),
    "depth":tk.StringVar(),
    "alti":tk.StringVar()
}
tk.Label(win, textvariable=tk_vars["status"]).grid(row=0,column=0,columnspan=2)
for i in range(len(tk_vars)):
    tk.Label(win, text=f"{tk_vars.keys()[i]} value :").grid(row=i+1,column=0)
    tk.Label(win, textvariable=tk_vars[i]).grid(row=i+1,column=1)

vidname = time.strftime('sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open("sm4000_received_data\\probes_data\\"+vidname,mode='w') as output_file:
    debug = True
    running = True
    while running:
        try:
            if debug:
                print("waiting for data...")
            data = i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti = client.recv(1024).decode().split(",")
            print( i,lvl_volt,bat_volt,temp,depth )
            output_file.write(data)
            output_file.flush()
        except:
            print("can't read incoming data")
            running = False

client.close()
print("socket closed\nDisconnected")

raise SystemExit

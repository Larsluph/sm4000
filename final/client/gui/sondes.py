#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard
import tkinter as tk

win = tk.Tk()
win.title = "GUI_sondes"

tk_vars = {
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

scroll = tk.Scrollbar(win)
scroll.grid(row=0,column=2)
debug_screen = tk.Text(win,yscrollcommand=scroll.set)
debug_screen.grid(row=0,column=0,columnspan=2)

scroll.config(command=debug_screen.yview)

for i in range(len(tk_vars)):
    tk.Label(win, text=f"{tk_vars.keys()[i]} value :").grid(row=i+1,column=0)
    tk.Label(win, textvariable=tk_vars[i]).grid(row=i+1,column=1)

try:
    ip = ("192.168.137.2","50003")

    tk_vars["status"].set(f"Connecting to {':'.join(ip)}...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ip)
    tk_vars["status"].set("Connected!")
except:
    tk_vars["status"].set("unable to connect to host")
    time.sleep(.5)
    tk_vars["status"].set("Exiting...")
    time.sleep(.5)
    win.destroy()
    raise SystemExit

try:
    os.system("mkdir sm4000_received_data\\probes_data")
except:
    pass

keyboard.add_hotkey('esc',lambda: exec("global running;running=False"),suppress=False)
tk_vars["status"].set("waiting for data...")

vidnpath = "sm4000_received_data\\probes_data\\" +  time.strftime('sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open(vidpath,mode='w') as output_file:
    debug = True
    running = True
    while running:
        try:
            if debug:
                tk_vars["status"].set("waiting for data...")
            data = i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti = client.recv(1024).decode().split(",")
           
            for i in "i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti".split(","):
                tk_vars[i].set(eval(i))
            output_file.write(data)
            output_file.flush()
            win.update_idletasks()
            win.update()
        except:
            tk_vars["status"].set("can't read incoming data")
            running = False

client.close()
tk_vars["status"].set("Disconnected")
win.destroy()

raise SystemExit
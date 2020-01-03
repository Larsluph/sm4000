#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time

import keyboard
import tkinter as tk

def update_window(window):
  window.update_idletasks()
  window.update()

def update_debug(window,text,msg):
  text.config(state=tk.NORMAL)
  text.insert(tk.END, f"\n{msg}")
  text.config(state=tk.DISABLED)
  text.see(tk.END)

  update_window(window)

win = tk.Tk()
win.title = "GUI_sondes"

tk_vars = {
  "i":tk.IntVar(),
  "t":tk.DoubleVar(),
  "delta_t":tk.DoubleVar(),
  "lvl_val":tk.IntVar(),
  "lvl_volt":tk.DoubleVar(),
  "bat_val":tk.IntVar(),
  "bat_volt":tk.DoubleVar(),
  "pressure":tk.DoubleVar(),
  "temp":tk.DoubleVar(),
  "depth":tk.DoubleVar(),
  "alti":tk.DoubleVar()
}

debug_screen = tk.Text(win,height=10,width=80,state=tk.DISABLED)
debug_screen.grid(row=1,column=0,columnspan=2)

i = 0
for var in list(tk_vars.keys()):
  tk.Label(win, text=f"{var} value :").grid(row=i+2,column=0)
  tk.Label(win, textvariable=tk_vars[var]).grid(row=i+2,column=1)
  i += 1

update_window(win)

try:
  ip = ("192.168.137.2",50003)

  update_debug(win,debug_screen,f"Connecting to {':'.join(map(str,ip))}...")
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect(ip)
  update_debug(win,debug_screen,"Connected!")
except:
  update_debug(win,debug_screen,"unable to connect to host")
  update_debug(win,debug_screen,"Exiting...")
  time.sleep(1)
  win.destroy()
  raise SystemExit

try:
  os.system("mkdir sm4000_received_data\\probes_data")
except:
  pass

keyboard.add_hotkey('esc',lambda: exec("global running;running=False"),suppress=False)
update_debug(win,debug_screen,"waiting for data...")

vidpath = "sm4000_received_data\\probes_data\\" + time.strftime('sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open(vidpath,mode='w') as output_file:
  debug = True
  running = True
  while running:
    try:
      data = i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti = client.recv(1024).decode().split(",")

      for x in "i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti".split(","):
        tk_vars[x].set(eval(x))
      output_file.write(data)
      output_file.flush()
      update_window(win)
    except:
      update_debug(win,debug_screen,"can't read incoming data")
      running = False

client.close()
update_debug(win,debug_screen,"Disconnected")
time.sleep(1)
win.destroy()

raise SystemExit

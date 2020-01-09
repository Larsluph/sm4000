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

def update_debug(window,text,msg,prefix="\n"):
  text.config(state=tk.NORMAL)
  text.insert(tk.END, f"{prefix}{msg}")
  text.config(state=tk.DISABLED)
  text.see(tk.END)

  update_window(window)

def update_log(file,data):
  file.write(data)
  file.flush()

def grid(win,var,coords):
  tk.Label(win, text=f"{var} value :").grid(row=coords[0]+1,column=coords[1]*2,sticky=tk.E)
  tk.Label(win, textvariable=tk_vars[var]).grid(row=coords[0]+1,column=coords[1]*2+1,sticky=tk.W)

win = tk.Tk()
win.title = "GUI sondes"

debug_screen = tk.Text(win,height=7,width=120,state=tk.DISABLED)
debug_screen.grid(row=0,column=0,columnspan=8)

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

grid_val = {
  "i":        (0,0),
  "t":        (1,0),
  "delta_t":  (2,0),
  "lvl_val":  (0,1),
  "lvl_volt": (1,1),
  "pressure": (2,1),
  "bat_val":  (0,2),
  "bat_volt": (1,2),
  "temp":     (2,2),
  "depth":    (0,3),
  "alti":     (1,3)
}

for i in grid_val.keys():
  grid(win,i,grid_val[i])

update_window(win)

try:
  ip = ("192.168.137.2",50003)

  update_debug(win,debug_screen,f"Connecting to {':'.join(map(str,ip))}...",prefix="")
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect(ip)
  client.settimeout(5.0)
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

vidpath = time.strftime('sm4000_received_data\\probes_data\\sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
with open(vidpath,mode='w') as output_file:
  running = True
  while running:
    try:
      data = i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti = client.recv(1024).decode().split(",")

      for x in "i,t,delta_t,lvl_val,lvl_volt,bat_val,bat_volt,pressure,temp,depth,alti".split(","):
        tk_vars[x].set(eval(x))

    except:
      data = "can't read incoming data"
      update_debug( win,debug_screen,str(sys.exc_info()[1]) )

    finally:
      update_log(output_file,data)
      update_debug(win,debug_screen,f"data n°{i} received!")

client.close()
update_debug(win,debug_screen,"Disconnected")
time.sleep(1)
win.destroy()

raise SystemExit

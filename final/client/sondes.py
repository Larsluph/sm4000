#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time
import tkinter as tk
from tkinter import DoubleVar, IntVar, StringVar

import keyboard


def update_window(window):
  window.update_idletasks()
  window.update()

def update_debug(window,text,msg,prefix="\n"):
  text.config(state=tk.NORMAL)
  text.insert(tk.END, f"{prefix}{msg}")
  text.config(state=tk.DISABLED)
  text.see(tk.END)

  update_window(window)

def update_log(logpath,data):
  with open(logpath,mode='a') as file:
    file.write(str(data)+"\n")

def update_vars(data):
  for x in data:
    if x in ["lvl_percent","bat_percent","int_humidity"]:
      tk_vars[x].set(str(data[x])+"%")
    else:
      tk_vars[x].set(data[x])

def grid(win,var,coords,font):
  tk.Label(win,font=font, text=f"{var} :").grid(row=coords[0]+1,column=coords[1]*2,sticky=tk.E)
  tk.Label(win,font=font, textvariable=tk_vars[var]).grid(row=coords[0]+1,column=coords[1]*2+1,sticky=tk.W)

win = tk.Tk()
win.title("GUI sondes")

font_debug = ('Helvetica', 11) # font used in the Text widget
font = ('Helvetica', 13) # font used elsewhere in tk

debug_screen = tk.Text(win,height=7,width=120,state=tk.DISABLED,font=font_debug)
debug_screen.grid(row=0,column=0,columnspan=10)

tk_vars = {
  "i"                :    IntVar(),
  "t"                : DoubleVar(),
  "delta_t"          : DoubleVar(),

  "lvl_val"          :    IntVar(),
  "lvl_volt"         : DoubleVar(),
  "lvl_percent"      : StringVar(),

  "bat_val"          :    IntVar(),
  "bat_volt"         : DoubleVar(),
  "bat_percent"      : StringVar(),

  "ext_pressure"     : DoubleVar(),
  "ext_temp"         : DoubleVar(),
  "ext_depth"        : DoubleVar(),
  "ext_alti"         : DoubleVar(),

  "int_pressure"     : DoubleVar(),
  "int_temp"         : DoubleVar(),
  "int_humidity"     : StringVar(),
  "dissolved_oxygen" : DoubleVar()
}

grid_val = {
  "i"                : (0,0),
  "t"                : (1,0),
  "delta_t"          : (2,0),

  "lvl_val"          : (0,1),
  "lvl_volt"         : (1,1),
  "lvl_percent"      : (2,1),

  "bat_val"          : (0,2),
  "bat_volt"         : (1,2),
  "bat_percent"      : (2,2),

  "ext_pressure"     : (0,3),
  "ext_temp"         : (1,3),
  "ext_depth"        : (2,3),
  "ext_alti"         : (3,3),

  "int_pressure"     : (0,4),
  "int_temp"         : (1,4),
  "int_humidity"     : (2,4),
  "dissolved_oxygen" : (3,4)
}

for i in grid_val.keys():
  grid(win,i,grid_val[i],font)

for x in ["lvl_percent","bat_percent","int_humidity"]:
  tk_vars[x].set("00.00%")
update_window(win)

try:
  # ip = ("192.168.137.2",50003)
  ip = ("192.168.0.31",50001)

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

log_path = time.strftime('sm4000_received_data\\probes_data\\sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
running = True
while running:
  try:
    cmd = client.recv(1024).decode()

  except:
    data = "can't read incoming data (client error)"
    update_debug( win,debug_screen,str(sys.exc_info()[1]) )

  else:
    try:
      eval(cmd)
    except:
      data = cmd
    else:
      data = eval(cmd)
      update_vars(data)

  finally:
    update_log(log_path,data)
    update_debug(win,debug_screen,data)

client.close()
update_debug(win,debug_screen,"Disconnected")
time.sleep(1)
win.destroy()

raise SystemExit

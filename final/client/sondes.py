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

def update_vars(data,tk_vars):
  for x in data:
    if x in ["lvl_percent","bat_percent","int_humidity"]:
      tk_vars[x].set(str(data[x])+"%")
    else:
      tk_vars[x].set(data[x])

def grid(win,var,font):
  for y in range(len(var)):
    for x in range(len(var[y])):
      varname = list( var[y].keys() )[x] # ="i"
      tk.Label(win,font=(font[0],font[1]*var[y][varname]), text=f"{varname} :").grid(row=x+1,column=y*2,sticky=tk.E)
      tk.Label(win,font=(font[0],font[1]*var[y][varname]), textvariable=tk_vars[varname] ).grid(row=x+1,column=y*2+1,sticky=tk.W)

win = tk.Tk()
win.title("GUI sondes")

font_debug = ('Helvetica', 11) # font used in the Text widget
font = ('Helvetica', 13) # font used elsewhere in tk

debug_screen = tk.Text(win,height=15,width=130,state=tk.DISABLED,font=font_debug)
debug_screen.grid(row=0,column=0,columnspan=10)

tk_vars = {
  "i"                :    IntVar(),
  "t"                : DoubleVar(),
  "delta_t"          : DoubleVar(),

  "lvl_val"          :    IntVar(),
  "lvl_volt"         : DoubleVar(),
  "lvl_percent"      : StringVar(),

  "tds_volt"         :    IntVar(),
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

grid_val = [
  {"i":1,"t":1,"delta_t":1},
  {"lvl_val":1,"lvl_volt":1,"lvl_percent":1},
  {"tds_volt":1,"bat_volt":1,"bat_percent":1},
  {"ext_temp":1,"ext_depth":1,"ext_alti":1},
  {"int_pressure":1,"int_temp":1,"int_humidity":1,"dissolved_oxygen":1}
] # gather all vars in line then in column with their magnification factor

grid(win,grid_val,font)

multi=4 # coef to enlarge
var="ext_pressure" # variable to enlarge
tk.Label(win,font=(font[0],font[1]*multi), text=f"{var} :").grid(row=4,column=0,columnspan=5,rowspan=2,sticky=tk.E)
tk.Label(win,font=(font[0],font[1]*multi), textvariable=tk_vars[var] ).grid(row=4,column=5,columnspan=3,rowspan=2,sticky=tk.W)

for x in ["lvl_percent","bat_percent","int_humidity"]:
  tk_vars[x].set("00.00%")
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
      update_vars(data,tk_vars)

  finally:
    update_log(log_path,data)
    update_debug(win,debug_screen,data)

client.close()
update_debug(win,debug_screen,"Disconnected")
time.sleep(1)
win.destroy()

raise SystemExit

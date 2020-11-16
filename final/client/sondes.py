#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import time
import tkinter as tk
from tkinter import DoubleVar, IntVar, StringVar

import keyboard

def update_window(window):
    "update Tk window"
    window.update_idletasks()
    window.update()

def update_debug(window, frame, msg, prefix="\n"):
    "update TK Text frame with {msg}"
    frame.config(state=tk.NORMAL) # make it writeable
    frame.insert(tk.END, f"{prefix}{msg}") # write msg
    frame.config(state=tk.DISABLED) # make it read-only
    frame.see(tk.END) # scroll to the bottom of the frame

    update_window(window)

def update_log(logpath, data):
    "update log file with {data}"
    if os.path.exists(logpath):
        with open(logpath, mode='a') as file:
            file.write(f"{data}\n")

def update_vars(data, tk_vars):
    "update {tk_vars} from data"
    for x in data:
        tk_vars[x]["value"].set(f"{data[x]}{tk_vars[x]['unit']}")

def sync_vars(filepath,to_sync):
    "sync data to add it to the camera's HUD"
    with open(filepath, "w") as f:
        f.write(str(to_sync))

def setup_grid(win, tkvars, var, font):
    "setup TK grid"
    for y in range(len(var)):
        for x in range(len(var[y])):
            tk.Label(win,font=font, text=f"{var[y][x]} :").grid(row=x+1,column=y*2,sticky=tk.E)
            tk.Label(win,font=font, textvariable=tk_vars[ var[y][x] ]["value"] ).grid(row=x+1,column=y*2+1,sticky=tk.W)

win = tk.Tk()
win.title("GUI sondes")

font_debug = ('Helvetica', 11) # font used in the Text widget
font = ('Helvetica', 14) # font used elsewhere in tk

debug_screen = tk.Text(win, height=15, width=130, state=tk.DISABLED, font=font_debug)
debug_screen.grid(row=0, column=0, columnspan=10)

tk_vars = {
    "i"                : { "value": StringVar(), "unit": "" },
    "t"                : { "value": StringVar(), "unit": "sec" },
    "delta_t"          : { "value": StringVar(), "unit": "sec" },

    "lvl_val"          : { "value": StringVar(), "unit": "" },
    "lvl_volt"         : { "value": StringVar(), "unit": "V" },
    "lvl_percent"      : { "value": StringVar(), "unit": "%" },

    "tds_volt"         : { "value": StringVar(), "unit": "V" },
    "bat_volt"         : { "value": StringVar(), "unit": "V" },
    "bat_percent"      : { "value": StringVar(), "unit": "%" },

    "ext_pressure"     : { "value": StringVar(), "unit": "mbar" },
    "ext_temp"         : { "value": StringVar(), "unit": "°C" },
    "ext_depth"        : { "value": StringVar(), "unit": "m" },
    "ext_alti"         : { "value": StringVar(), "unit": "m" },

    "int_pressure"     : { "value": StringVar(), "unit": "Pa" },
    "int_temp"         : { "value": StringVar(), "unit": "°C" },
    "int_humidity"     : { "value": StringVar(), "unit": "%" },
    "dissolved_oxygen" : { "value": StringVar(), "unit": "mg/L" },
}

grid_val = [
    ["i", "t", "delta_t"],
    ["lvl_val", "lvl_volt", "lvl_percent"],
    ["tds_volt", "bat_volt", "bat_percent"],
    ["ext_pressure", "ext_temp", "ext_depth", "ext_alti"],
    ["int_pressure", "int_temp", "int_humidity", "dissolved_oxygen"]
] # gather all vars in column then in line
"""
[
    column1: [line1, line2, ...],
    column2: [line1, line2, ...],
    ...
]
"""

setup_grid(win, tk_vars, grid_val, font)

to_sync = ["lvl_percent", "bat_percent", "int_humidity"] # vars to sync with the HUD
for x in to_sync:
    tk_vars[x]["value"].set("00.00")
update_window(win)

try:
    ip = ("192.168.137.2", 50003)

    update_debug(win, debug_screen, f"Connecting to {':'.join(map(str, ip))}...", prefix="")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ip)
    client.settimeout(5.0)
    update_debug(win, debug_screen, "Connected!")
except:
  update_debug(win,debug_screen, "unable to connect to host")
  update_debug(win,debug_screen, "Exiting...")
  time.sleep(1)
  win.destroy()
  raise SystemExit

try:
  os.system("mkdir sm4000_received_data\\probes_data")
except:
  pass

keyboard.add_hotkey('esc', lambda: exec("global running;running=False"), suppress=False)
update_debug(win, debug_screen, "waiting for data...")

log_path = time.strftime('sm4000_received_data\\probes_data\\sm4000_probes_data_%Y-%m-%d_%H-%M-%S.txt')
running = True
while running:
  try:
    cmd = client.recv(1024).decode()

  except:
    data = "can't read incoming data (client error)"
    update_debug(win, debug_screen, str(sys.exc_info()[1]))

  else:
    try:
      eval(cmd)
    except:
      data = cmd
    else:
      data = eval(cmd)
      update_vars(data, tk_vars)
      sync_vars("var_sync.txt", {x: tk_vars[x]["value"].get() for x in to_sync})

  finally:
    update_log(log_path, data)
    update_debug(win, debug_screen, data)

os.remove("var_sync.txt")
client.close()
update_debug(win,debug_screen, "Disconnected")
time.sleep(1)
win.destroy()

raise SystemExit

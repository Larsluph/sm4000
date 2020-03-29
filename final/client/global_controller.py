#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import socket
import sys
import time
import tkinter as tk

import keyboard
import pygame
import pygame.joystick

from tkinter import BooleanVar, DoubleVar, IntVar, StringVar

############
## CLASSs ##
############

class Vars:
  # class to store all variables data
  def __init__(self):
    self.running = True # infinite loop controller

    self.gui_check = True # GUI activator

    self.dir = { # dict send to drone
      "powered" : False,
      "left" : 0,
      "right" : 0,
      "y" : 0,
      "light_pow" : False,
      "lights" : 0
    }
    self.pwr = dict()
    self.pos = 100
    self.threshold = .2 # joy deadzone
    self.light_step = self.pos

    self.key_init = False
    self.joy_init = False

    return

  def key_vars(self):
    self.gui_check = False
    self.win.destroy()

    self.key_init = True
    self.joy_init = False

    return

  def joy_vars(self):
    self.key_init = False
    self.joy_init = True
    self.joy = pygame.joystick.Joystick(0)
    self.joy.init()
    check_joy(self)

    self.boosted = False
    self.latest = self.dir.copy()
    self.axes = tuple()
    self.buttons = tuple()

    return

  def gui_setup(self):
    self.win = tk.Tk()
    self.win.wm_attributes("-topmost",1)
    self.win.title("global controller GUI")

    self.font_debug = ('Helvetica', 11) # font used in the Text widget
    self.font = ('Helvetica', 20) # font used elsewhere in tk

    self.debug_screen = tk.Text(self.win,height=14,width=96,state=tk.DISABLED,font=self.font_debug) # Text widget to display all debug data
    self.debug_screen.grid(row=0,column=0,columnspan=14)

    # dict with all tk vars used in GUI
    self.tk_vars = {
      "left": IntVar(),
      "right": IntVar(),
      "y": IntVar(),
      "lights" : IntVar(),
      # ^- = dir

      "axes": (
        DoubleVar(),
        DoubleVar(),
        DoubleVar(),
        IntVar() # hat[1]
      ),
      "buttons": (
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar(),
        BooleanVar()
      )
    }

    self.tk_lbls = {
      "powered":   None,
      "light_pow": None,
      "boosted":   None
    }

    self.grid_val = {
      "left":      ( (1,0,1),(1,1,1) ),
      "right":     ( (2,0,1),(2,1,1) ),
      "y":         ( (1,4,1),(1,5,3) ),
      "lights" :   ( (1,8,4),(1,12,2) )
    }

    self.grid_val_lbls = {
      "powered":   ( (0,0,1),(0,1,1) ),
      "light_pow": ( (0,8,4),(0,12,2) ),
      "boosted":   ( (0,2,4),(0,6,2) )
    }

    for x in self.grid_val.keys():
      grid(self,x,self.grid_val[x])

    for x in self.grid_val_lbls.keys():
      grid_lbls(self,x,self.grid_val_lbls[x])

    grid_spec(self)

    return

###########
## FUNCs ##
###########

def prompt_popup(window,title,msg):
  global prompt_win, user_entry, user_input
  prompt_win = tk.Toplevel(master=window)
  prompt_win.wm_attributes("-topmost",1)
  prompt_win.title(title)
  prompt_win.protocol("WM_DELETE_WINDOW",lambda:exec("pass"))
  tk.Label(prompt_win,text=msg).grid(row=0,column=0)
  user_entry = tk.Entry(prompt_win,width=3)
  user_entry.grid(row=0,column=1)
  prompt_win.bind("<Return>",callback_prompt)
  tk.Button(prompt_win,text="Validate!",command=callback_prompt).grid(row=1,columnspan=2)

  user_entry.focus_force()
  prompt_win.wait_window()
  try:
    output = user_input
  except:
    print("Action cancelled by user\nExiting...")
    raise SystemExit
  del prompt_win, user_entry, user_input
  return output

def callback_prompt(*args,**kwargs):
  global prompt_win, user_entry, user_input
  user_input = user_entry.get()
  errors = list()

  if not(user_input.lower() in ["n","y","no","yes"]):
    errors.append("invalid_data")
    user_entry.delete(0,tk.END)
    user_entry.insert(0,"invalid data entered (y/n)")

  if errors == []:
    if user_input.lower() in ["y","yes"]:
      user_input = 1
    else:
      user_input = 0
    prompt_win.destroy()

def update_dir(data):
  pygame.event.get()
  data.axes = (
    round(data.joy.get_axis(0),2),
    round(-data.joy.get_axis(1),2),
    round(data.joy.get_axis(2),2),
    round(data.joy.get_axis(3),2),
    data.joy.get_hat(0)
  )

  data.buttons = (
    None,
    data.joy.get_button(0),
    data.joy.get_button(1),
    data.joy.get_button(2),
    data.joy.get_button(3),
    data.joy.get_button(4),
    data.joy.get_button(5),
    data.joy.get_button(6),
    data.joy.get_button(7),
    data.joy.get_button(8),
    data.joy.get_button(9),
    data.joy.get_button(10),
    data.joy.get_button(11)
  )

  coef = 5 if data.boosted else 2
  data.pwr = {
    "x": int( abs( round(data.axes[0],2) ) * coef),
    "y": int( abs( round(data.axes[1],2) ) * coef),
    "lights": int(abs(data.axes[2] - 1) * 5)
  }

def update_tkvars(data):
  # update all GUI labels

  # skip update if gui disabled
  if not(data.gui_check):
    return

  ### powered,light_pow,boosted
  for x in data.tk_lbls.keys():
    check = bool(data.dir[x]) if x in data.dir else bool(data.boosted) # boosted is the only bool not in dir
    bg = "#00FF00" if check else "#FF0000"
    # set lbl bg color to either green or red based on vars
    data.tk_lbls[x].config(bg=bg)
    del bg

  ### left,right,y,lights
  for x in data.grid_val.keys():
    data.tk_vars[x].set(data.dir[x])

  ### axes x,z,slider
  for i in range(len(data.axes)-2):
    data.tk_vars["axes"][i].set(data.axes[i]) # update all axes except joy rot & hat
  ### axe y
  data.tk_vars["axes"][3].set(data.axes[4][1]) # only z in hat updated

  ### buttons
  for i in range(len(data.buttons)-1):
    data.tk_vars["buttons"][i].set(data.buttons[i+1]) # update all buttons

  update_window(data.win) # update window to display all lbls updates

  return

def update_window(window):
  window.update_idletasks()
  window.update()
  return

def update_debug(data,msg,prefix="\n"):
  if data.gui_check:
    data.debug_screen.config(state=tk.NORMAL)
    data.debug_screen.insert(tk.END, f"{prefix}{msg}")
    data.debug_screen.config(state=tk.DISABLED)
    data.debug_screen.see(tk.END)

    update_window(data.win)
    return

  else:
    print(msg)
    return

def grid(data,var,coords):
  # coords = ( (0,0,0),(0,0,0) )
  #             label , value
  tk.Label(data.win, text=f"{var} :", font=data.font).grid(row=coords[0][0]+1,column=coords[0][1],columnspan=coords[0][2],sticky=tk.E)
  tk.Label(data.win, textvariable=data.tk_vars[var], font=data.font).grid(row=coords[1][0]+1,column=coords[1][1],columnspan=coords[1][2],sticky=tk.W)

  return

def grid_lbls(data,var,coords):
  tk.Label(data.win, text=f"{var} :", font=data.font).grid(row=coords[0][0]+1,column=coords[0][1],columnspan=coords[0][2],sticky=tk.E)
  data.tk_lbls[var] = tk.Label(data.win, text="            ",bg="#FF0000", font=data.font)
  data.tk_lbls[var].grid(row=coords[1][0]+1,column=coords[1][1],columnspan=coords[1][2])

  return

def grid_spec(data):
  tk.Label(data.win, text="Axes :", font=data.font).grid(row=4,column=0,columnspan=2,sticky=tk.E)
  for i in range(len(data.tk_vars["axes"])):
    tk.Label(data.win, textvariable=data.tk_vars["axes"][i], font=data.font).grid(row=4,column=2+i*3,columnspan=3)

  tk.Label(data.win, text="Buttons pressed :", font=data.font).grid(row=5,column=0,columnspan=2,sticky=tk.E)
  for i in range(len(data.tk_vars["buttons"])):
    tk.Label(data.win, textvariable=data.tk_vars["buttons"][i], font=data.font).grid(row=5,column=2+i)

  return

def check_joy(data):
  pygame.event.get()
  msg="\n".join([
    f"id       {str(data.joy.get_id())}",
    f"name     {str(data.joy.get_name())}",
    f"axes     {str(data.joy.get_numaxes())}",
    f"buttons  {str(data.joy.get_numbuttons())}",
    f"hats     {str(data.joy.get_numhats())}",
    f"balls    {str(data.joy.get_numballs())}"]
  )
  update_debug(data,msg)
  time.sleep(1)

def wait_button(joy,id):
  while joy.get_button(id-1):
    pygame.event.get()

    continue

def forward(data):
  data.dir["left"] += +data.pos
  data.dir["right"] += +data.pos
  send(data)

def backward(data):
  data.dir["left"] += -data.pos
  data.dir["right"] += -data.pos
  send(data)

def turn_left(data):
  data.dir["left"] += -data.pos
  data.dir["right"] += +data.pos
  send(data)

def turn_right(data):
  data.dir["left"] += +data.pos
  data.dir["right"] += -data.pos
  send(data)

# def left(data):
#   pass

# def right(data):
#   pass

def up(data):
  data.dir["y"] += +200
  # data.dir["y"] += +data.pos
  send(data)

def down(data):
  data.dir["y"] += -200
  # data.dir["y"] += -data.pos
  send(data)

def stop(data):
  data.dir["left"] = 0
  data.dir["right"] = 0
  data.dir["y"] = 0
  send(data)

def light_mgmt(data,operator,reset):
  if not(reset):
    if operator == "+":
      data.dir["lights"] += data.light_step
    else:
      data.dir["lights"] -= data.light_step
  else:
    data.dir["light_pow"] = not(data.dir["light_pow"])
  send(data)

def toggle_pwr(data):
  data.dir['powered'] = not(data.dir['powered'])
  send(data)

def send(data):
  cmd = "/" + str(data.dir)
  if net_check:
    client.send(cmd.encode("Utf8"))

  update_debug(data,data.dir)

##################
## MAIN PROGRAM ##
##################

data = Vars() # define vars storage
if data.gui_check:
  data.gui_setup() # setup gui if enabled

update_debug(data,"net check",prefix="")
net_check = bool(prompt_popup(data.win,"net check","Do you want to check network connection ? (yes/no)"))

if net_check:
  ip = ("192.168.137.2",50001)

  update_debug(data,f"Connecting to {ip[0]}:{ip[1]}...")
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect(ip)
  update_debug(data,"Connected!")
else:
  update_debug(data,"ignoring...")

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
  joytest = 0
else:
  update_debug(data,"joystick check")
  joytest = bool(prompt_popup(data.win,"joystick check","Do you want to use joystick ? (yes/no)"))

if joytest:
  # joy_control
  data.joy_vars()
  update_debug(data,"joystick ready")
  update_debug(data,"Waiting for instructions...")

  while data.running:
    update_dir(data)

    if data.buttons[1] == 0:
      # top
      if (-data.threshold < data.axes[0] < +data.threshold) and (data.axes[1] > +data.threshold):
        data.dir["left"] = (+data.pos) * data.pwr["y"]
        data.dir["right"] = (+data.pos) * data.pwr["y"]

      # top right
      elif (data.axes[0] > +data.threshold) and (data.axes[1] > +data.threshold):
        data.dir["left"] = (+data.pos * 1.5) * data.pwr["x"]
        data.dir["right"] = (+data.pos * .5) * data.pwr["x"]

      # right
      elif (data.axes[0] > +data.threshold) and (-data.threshold < data.axes[1] < +data.threshold):
        data.dir["left"] = (+data.pos) * data.pwr["x"]
        data.dir["right"] = (-data.pos) * data.pwr["x"]

      # bottom right
      elif (data.axes[0] > +data.threshold) and (data.axes[1] < -data.threshold):
        data.dir["left"] = (-data.pos * 1.5) * data.pwr["x"]
        data.dir["right"] = (-data.pos * .5) * data.pwr["x"]

      # bottom
      elif (-data.threshold < data.axes[0] < +data.threshold) and (data.axes[1] < -data.threshold):
        data.dir["left"] = (-data.pos) * data.pwr["y"]
        data.dir["right"] = (-data.pos) * data.pwr["y"]

      # bottom left
      elif (data.axes[0] < -data.threshold) and (data.axes[1] < -data.threshold):
        data.dir["left"] = (-data.pos * .5) * data.pwr["x"]
        data.dir["right"] = (-data.pos * 1.5) * data.pwr["x"]

      # left
      elif (data.axes[0] < -data.threshold) and (-data.threshold < data.axes[1] < +data.threshold):
        data.dir["left"] = (-data.pos) * data.pwr["x"]
        data.dir["right"] = (+data.pos) * data.pwr["x"]

      # top left
      elif (data.axes[0] < -data.threshold) and (data.axes[1] > +data.threshold):
        data.dir["left"] = (+data.pos * .5) * data.pwr["x"]
        data.dir["right"] = (+data.pos * 1.5) * data.pwr["x"]

      elif (-data.threshold < data.axes[0] < +data.threshold) and (-data.threshold < data.axes[1] < +data.threshold):
        data.dir["left"] = 0
        data.dir["right"] = 0

      data.dir["y"] = 300*data.axes[4][1]

      if data.buttons[2] == 1:
        data.boosted = not(data.boosted)
        wait_button(data.joy,2)

      elif data.buttons[4] == 1:
        data.dir["light_pow"] = not(data.dir["light_pow"])
        wait_button(data.joy,4)

      elif data.buttons[11] == 1:
        data.dir['powered'] = not(data.dir['powered'])
        wait_button(data.joy,11)

      elif data.buttons[12] == 1:
        update_debug(data,"stopping transmission...")
        data.dir["powered"] = False
        data.running = False

      data.dir["lights"] = data.light_step * data.pwr["lights"]

      if data.latest != data.dir:
        data.latest = data.dir.copy()
        send(data)

    update_tkvars(data)

  if net_check:
    client.send("'exit'".encode("Utf8"))
    client.close()

  update_debug(data,"END OF PROGRAM")
  time.sleep(0.5)

  if data.gui_check:
    data.win.destroy()
  raise SystemExit

else:
  data.key_vars()
  # key_control
  keyboard.add_hotkey('z',forward,args=[data],suppress=True)
  keyboard.add_hotkey('s',backward,args=[data],suppress=True)
  keyboard.add_hotkey('q',turn_left,args=[data],suppress=True)
  keyboard.add_hotkey('d',turn_right,args=[data],suppress=True)
  keyboard.add_hotkey('shift',up,args=[data],suppress=True)
  keyboard.add_hotkey('ctrl',down,args=[data],suppress=True)
  keyboard.add_hotkey('space',stop,args=[data],suppress=True)
  keyboard.add_hotkey('enter',toggle_pwr,args=[data],suppress=True)
  keyboard.add_hotkey('*',light_mgmt,args=[data,"+",False],suppress=True)
  keyboard.add_hotkey('ù',light_mgmt,args=[data,"-",False],suppress=True)
  keyboard.add_hotkey('$',light_mgmt,args=[data,0,True],suppress=True)

  print("\nkeyboard ready")
  print("Waiting for instructions...")
  keyboard.wait('esc')

  print("stopping transmission...")
  keyboard.clear_all_hotkeys()

  if net_check:
    client.send("'exit'".encode("Utf8"))
    client.close()

  print("END OF PROGRAM")
  time.sleep(0.5)

  raise SystemExit

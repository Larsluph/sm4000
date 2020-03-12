#!/usr/bin/env python3
#-*- coding:utf-8 -*-

ip = {
  "propulsion" : ('192.168.137.2',50001),
  "camera"     : ('192.168.137.2',50002),
  "sondes"     : ('192.168.137.2',50003)
}

pin_id = {
  "left": 0,
  "y": 1,
  "right": 2,
  "lights": 16
}

i2c_address = {
  "ads_water": 0x48,
  "ads_battery": 0x49,
  "oxygen": 0x61,
  "pres_temp_external": 0x76,
  "pres_temp_internal": 0x77
}

probes_checks = {
  "networking"    : 1,
  "water_lvl"     : 0,
  "battery_cells" : 1,
  "ext_pres_temp" : 1,
  "oxygen"        : 1,
  "int_pres_temp" : 1
}

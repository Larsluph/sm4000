#!/usr/bin/env bash

python3 /media/pi/didier/propulsion.py&
sleep 1
python3 /media/pi/didier/camera.py&
sleep 1
python3 /media/pi/didier/sondes.py&

exit 1
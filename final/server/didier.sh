#!/usr/bin/env bash

python3 ~/Desktop/final/propulsion.py&
sleep 1
python3 ~/Desktop/final/camera.py&
sleep 1
python3 ~/Desktop/final/sondes.py&

exit 1

#!/bin/bash

#sudo chmod +x setup-hostname.sh

sudo apt-get update
sudo apt-get upgrade # update apt-get

sudo apt-get install avahi-daemon # install avahi to enable hostnames

sudo nano /etc/hosts # edit file with the wanted hostname (default: raspberrypi)
sudo nano /etc/hostname # same

sudo /etc/init.d/hostname.sh # commit changes

sudo reboot # reboot to take effect

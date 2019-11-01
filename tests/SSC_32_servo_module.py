#-------------------------------------------------------------------------------
# Name:        SSC-32 servo manager module
# Purpose:
#
# Author:      Stephane Ramstein
#
# Created:     26/08/2014
# Copyright:   (c) Stephane Ramstein 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# This module contains functions to manages the servos of a SSC32 card, play movements sequences and import them from csv files.
# A sequence is a list of steps which are lists of tuples for each servo to move to a position.
#
# [[time of the step 0, [(id of the first servo, his position, his speed), (id of the second servo, his position, his speed), ..., (id of the last servo, his position, his speed)],
# [time of the step 1, [(id of the first servo, his position, his speed), (id of the second servo, his position, his speed), ..., (id of the last servo, his position, his speed)],
# ...
# [time of the last step, [(id of the first servo, his position, his speed), (id of the second servo, his position, his speed), ..., (id of the last servo, his position, his speed)]]

import serial #module for com port use
import time #module for time management
import os #module for files management
import csv #module for csv files management

def sequence_from_csv_file(file_name = 'file_name.csv', sequence_name = 'sequence_name'):
    file = open(file_name) #open the file 'file_name'
    data_from_file = csv.reader(file) #convert the file into csv object
    sequence = []
    for row in data_from_file: #scan each row of the csv object
        if (data_from_file.line_num == 1): #the first row is the headers of the columns : sequence name, time, speed, servos identifiers
            header = row
        else: #the others are splits to shape the data to suited format
            if (row[0] == sequence_name): #test if the row correspond to a step with the good sequence name
                parameters = row[0:3] #the first 3 elements are the parameters : name of the sequence, time and speed
                all_positions = row[3:] #the others are the servos positions
                i = 0
                servo_parameters = []
                while (i < len(all_positions)): #scan the servos positions
                    servo_parameters.append((int(header[i + 3]), int(all_positions[i]), int(parameters[2]))) #build the sequence of tuples (servo id, position, speed) for each servo of a step
                    i = i + 1
                sequence.append([int(parameters[1]), servo_parameters]) #append the sequence with the time of the step and the sequence of tuples for each servo
    file.close() #close the file
    return sequence #return the builded sequence

def move(com_port, id, position, speed):
    "Function which moves the servo whith id 'id' to the position 'position' at speed 'speed'."
    data_to_send = '#' + str(id) + ' P' + str(position) + ' S' + str(speed) + chr(13) #a serial string to send to the com port. The instruction move the servo id with position and speed parameters.
    com_port.write(data_to_send.encode('ascii')) #send the serial string to the card

def center_all(com_port, speed):
    "Function which centers all the servos of the card to the position 1500 at speed 'speed'."
    for i in range(32):
        move(com_port, i, 1500, speed)

def move_one_step(com_port, sequence_of_servos_tuples):
    'Function which moves all the servos of a step.'
    for servo_tuple in sequence_of_servos_tuples:
        move(com_port, servo_tuple[0], servo_tuple[1], servo_tuple[2])

def move_sequence(com_port, sequence):
    "Function which move the servos according to a sequence."
    for step in sequence:
        move_one_step(com_port, step[1])
        time.sleep(step[0]/1000)

def disable_torque(com_port, id):
    "Function which disables the torque of a servo."
    data_to_send = '#' + str(id) + ' P0' + chr(13) #The instruction disables the torque of the servo id. To enable torque apply a position to the servo with the move function.
    com_port.write(data_to_send.encode('ascii'))

def disable_torque_all(com_port):
    "Function which disables the torque of all the servo of the card."
    for i in range(32):
        disable_torque(com_port, id)
#-------------------------------------------------------------------------------
# Name:        SSC-32 Sequencer
# Purpose:
#
# Author:      Stephane Ramtein
#
# Created:     26/08/2014
# Copyright:   (c) Stephane Ramstein 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from SSC_32_servo_module import * #module with dedicated SSC32 card functions
import serial #module for com port use
import time #module for time management

#-------------------------------------------------------------------------------
# Main program
#-------------------------------------------------------------------------------

com_port = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)

##data_to_send = 'ver' + chr(13) #a serial string to send to the com port. The instruction ask the firmware version of the SSC32 card
##com_port.write(data_to_send.encode('ascii')) #send the serial string to the card
##
##incoming_data = com_port.readline() #read the bytes incoming to the com port. It's an object of class 'bytes'
##print(incoming_data.decode('ascii')) #decode decode the bytes into ascii. We get an object of class 'str'

##center_all(com_port, 3000) #SSC32 card function which center (position 1500) all the servos with a speed of 3000
##time.sleep(2) #wait 2s

move(com_port, 16, 1800, 3000)
time.sleep(2) #wait 2s

com_port.close() #close the serial port 'comXX'

print('end of the main')

#-------------------------------------------------------------------------------
# End of the main program
#-------------------------------------------------------------------------------

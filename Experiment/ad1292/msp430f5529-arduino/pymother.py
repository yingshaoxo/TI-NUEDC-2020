"""
author: yingshaoxo
gmail: yingshaoxo@gmail.com
ls -l /dev/ttyUSB0
sudo usermod -a -G uucp yingshaoxo
sudo chmod a+rw /dev/ttyUSB0
"""
import matplotlib.pyplot as plt
import time
import numpy as np
import serial
import binascii
from time import sleep
from struct import pack, unpack


def int_to_byte(integer):
    hex_string = '{:02x}'.format(integer)
    a_byte = binascii.unhexlify(hex_string)
    return a_byte


def byte_to_int(a_byte):
    hex_string = binascii.hexlify(a_byte)
    integer = int(hex_string, 16)
    return integer


def byte_to_string(a_byte, length=2):
    return format(byte_to_int(a_byte), "02X").zfill(length)


ser = serial.Serial('/dev/ttyACM1', 115200)  # open serial port
print(ser.name)         # check which port was really used

import matplotlib.pyplot as plt
from drawnow import drawnow

def make_fig():
    plt.scatter(x, y)  # I think you meant this

plt.ion()  # enable interactivity
fig = plt.figure()  # make a figure


x = list()
y = list()
i = 0
while 1:
    i+=1
    if i > 5000:
        i = 0
    if ser.readable():
        two_byte = ser.read(2)
        if two_byte.hex() == "0afa":
            the_bytes = two_byte + ser.read(12)

            ecg = unpack("h", the_bytes[5:7])
            s32DaqVals = unpack("i", the_bytes[7:11])
            heart_rate = unpack("B", the_bytes[11:12])

            if heart_rate[0] != 0:
                print(ecg, s32DaqVals, heart_rate)

            x.append(i)
            y.append(ecg)  # or any arbitrary update to your figure's data
            x = x[-1000:]
            y = y[-1000:]
            drawnow(make_fig)

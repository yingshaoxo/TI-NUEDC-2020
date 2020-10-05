"""
author: yingshaoxo
gmail: yingshaoxo@gmail.com
ls -l /dev/ttyUSB0
sudo usermod -a -G uucp yingshaoxo
sudo chmod a+rw /dev/ttyUSB0
"""
import pandas as pd
import time
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


# ser = serial.Serial('/dev/ttyACM1', 115200)  # open serial port
ser = serial.Serial('COM4', 115200)  # open serial port
print(ser.name)         # check which port was really used

ser.
exit()


myDataFrame = pd.DataFrame(columns=['ecg', "a", "b1", "b2", "c1", "c2", "c3",
                                    "c4", "hear_rate", 'ECG', "A", "B1", "B2", "C1", "C2", "C3", "C4", "HEAR_RATE", "float_c", "float_c1", "float_c2"])

i = 0
while 1:
    i += 1
    if i > 5000:
        myDataFrame.to_excel("samples.xlsx")
        break
        i = 0
    if ser.readable():
        the_bytes = ser.readline()
        if (len(the_bytes) == 14):
            # print(str(ubinascii.hexlify(bytes_)))

            ecg = unpack("h", the_bytes[5:7])
            a = unpack("i", the_bytes[7:11])
            b1 = unpack("h", the_bytes[7:9])
            b2 = unpack("h", the_bytes[9:11])
            c1 = unpack("b", the_bytes[7:8])
            c2 = unpack("b", the_bytes[8:9])
            c3 = unpack("b", the_bytes[9:10])
            c4 = unpack("b", the_bytes[10:11])
            heart_rate = unpack("b", the_bytes[11:12])

            ECG = unpack("H", the_bytes[5:7])
            A = unpack("I", the_bytes[7:11])
            B1 = unpack("H", the_bytes[7:9])
            B2 = unpack("H", the_bytes[9:11])
            C1 = unpack("B", the_bytes[7:8])
            C2 = unpack("B", the_bytes[8:9])
            C3 = unpack("B", the_bytes[9:10])
            C4 = unpack("B", the_bytes[10:11])
            HEART_RATE = unpack("B", the_bytes[11:12])

            float_c = unpack("f", the_bytes[7:11])
            float_c1 = unpack("e", the_bytes[7:9])
            float_c2 = unpack("e", the_bytes[9:11])

            #seperator = "____"
            # print(ecg, seperator, a, seperator, b1, b2, seperator, c1,
            #      c2, c3, c4, seperator, ecg, heart_rate, "##########", ECG, seperator, A, seperator, B1, B2, seperator, C1, C2, C3, C4, "########", float_c, float_c1, float_c2)

            to_append = [ecg, a, b1, b2, c1, c2, c3, c4, heart_rate,
                         ECG, A, B1, B2, C1, C2, C3, C4, HEART_RATE, float_c, float_c1, float_c2]
            to_append = [e[0] for e in to_append]
            a_series = pd.Series(to_append, index=myDataFrame.columns)
            myDataFrame = myDataFrame.append(a_series, ignore_index=True)

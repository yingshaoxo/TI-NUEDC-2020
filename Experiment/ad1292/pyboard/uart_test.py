"""
We handle ad1292 here
"""


from struct import pack, unpack
from machine import UART
import ubinascii


import utime
import random
from lcd_library import *


print("\n\n\n")
print("start")


def hexlify(bytes_):
    return str(ubinascii.hexlify(bytes_))[2:-1]


class TwoWindow():
    def __init__(self):
        self.LCD = MyLCD(portrait=False)
        self.chars = Chars(color=BLACK, font="Arial_14", portrait=False)

        self.width = 320
        self.height = 240//2

    def map(self, x, i_m, i_M, o_m, o_M):
        return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

    def get_filtered_value(self, id_, value):
        pass

    def draw_at_the_upper_window(self, value):
        pass


twoWindow = TwoWindow()

# tx: x9
# rx: x10
ser = UART(1, 115200, bits=8, parity=None, stop=1, flow=0, timeout=0,
           timeout_char=2, rxbuf=64)                         # init with given baudrate
i = 0
while 1:
    i += 1
    if i > 1000:
        i = 0

    if ser.any():
        heading1 = ser.read(1)
        if hexlify(heading1) == "0a":
            heading2 = ser.read(1)
            if hexlify(heading2) == "fa":
                data_length_bytes = ser.read(2)
                data_length = unpack("H", data_length_bytes)[0]
                # print(data_length)
                type_bytes = ser.read(1)
                type_ = unpack("B", type_bytes)[0]
                if type_ == 2:
                    data_bytes = ser.read(data_length)
                    data = unpack("<iiB", data_bytes)
                    ecg, resp, heart_rate = data
                    #print(ecg, resp, heart_rate)
                    twoWindow.draw_at_the_upper_window1(ecg)
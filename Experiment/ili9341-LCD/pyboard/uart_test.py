"""
We handle ad1292 here
"""


from struct import pack, unpack
from machine import UART
import ubinascii


import utime
import random
from lcd_library import *


print("\n")
print("start")


def hexlify(bytes_):
    return str(ubinascii.hexlify(bytes_))[2:-1]


class TwoWindow():
    def __init__(self):
        self.LCD = MyLCD(portrait=False)
        self.LCD.fillScreen(BLACK)

        self.width = 320
        self.height = 240

        self.data_table = {
            "ecg": [],
            "ecgMin": -10000,
            "ecgMax": 10000,
            "resp": [],
            "respMin": -10000,
            "respMax": 10000,
        }

        self.x = 0
        self.last_y1 = 0
        self.last_y2 = 0

    def _map(self, x, i_m, i_M, o_m, o_M):
        return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

    def get_filtered_value(self, id_, value):
        kernel = 1

        self._preprocessing_before_drawing(id_, value)
        value = self._map(
            value, self.data_table[id_+"Min"], self.data_table[id_+"Max"], 0, self.height)

        self.data_table[id_].append(value)
        self.data_table[id_] = self.data_table[id_][-kernel:]

        self.x += 1
        if (self.x > 320):
            self.x = 1
            self.last_y, self.last_y2 = 0, 0
            self.data_table[id_+"Min"] = 0
            self.data_table[id_+"Max"] = 0

        return self.x, sum(self.data_table[id_]) // kernel

    def _preprocessing_before_drawing(self, id_, value):
        if value > self.data_table[id_+"Max"]:
            self.data_table[id_+"Max"] = value#(self.data_table[id_+"Max"] + value) // 2
        elif value < self.data_table[id_+"Min"]:
            self.data_table[id_+"Min"] = value#(self.data_table[id_+"Min"] + value) // 2

    def draw_at_the_upper_window(self, value):
        id_ = "ecg"

        filtered_x, filtered_y = self.get_filtered_value(id_, value)

        self.clean_screen(filtered_x+1)
        #self.LCD.drawPixel(filtered_x, filtered_y//2, RED)
        if (self.last_y1 != 0):
            self.LCD.drawLine(filtered_x-1, self.last_y1,
                              filtered_x, filtered_y//2, RED)
        self.last_y1 = filtered_y//2

    def draw_at_the_lower_window(self, value):
        id_ = "resp"

        filtered_x, filtered_y = self.get_filtered_value(id_, value)

        #self.LCD.drawPixel(filtered_x, filtered_y//2+self.height//2, RED)
        if (self.last_y2 != 0):
            self.LCD.drawLine(filtered_x-1, self.last_y2+self.height //
                              2,  filtered_x, filtered_y//2+self.height//2, RED)
        self.last_y2 = filtered_y//2

    def clean_screen(self, x=None, y=0):
        if x == None:
            self.LCD.drawRect(0, 0, self.width, self.height,
                              BLACK, border=0, infill=BLACK)
        else:
            if (x > 320):
                x = -1
            x += 1
            self.LCD.drawVline(x, y, self.height, BLACK, width=2)


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
                    data = unpack(">iiB", data_bytes)
                    ecg, resp, heart_rate = data
                    ecg //= 1000
                    resp //= 1000
                    #print(ecg, resp, heart_rate)
                    twoWindow.draw_at_the_upper_window(ecg)
                    twoWindow.draw_at_the_lower_window(resp)

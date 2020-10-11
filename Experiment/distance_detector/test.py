# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!

import sensor, image, time
from struct import pack, unpack

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.

from pyb import UART
import ubinascii
from time import sleep
import random

def bytes_to_hex(a_byte):
    return str(ubinascii.hexlify(a_byte))[2:-1]

def hex_to_bytes(hex_string):
    return ubinascii.unhexlify(hex_string)

def int_to_hex(integer, length=None):
    if length != None:
        hex_string = ('{:0'+str(length)+'X}').format(integer)
    else:
        hex_string = hex(integer)[2:]
        if (len(hex_string) % 2 == 1):
            hex_string = "0" + hex_string
    return hex_string

def hex_to_int(hex_string):
    return int(hex_string, 16)

def int_to_bytes(integer, length=None):
    hex_string = int_to_hex(integer, length)
    return hex_to_bytes(hex_string)

def bytes_to_int(a_byte):
    hex_string = bytes_to_hex(a_byte)
    return hex_to_int(hex_string)

def text_to_hex(text):
    length = len(text)*2
    bytes_ = ubinascii.hexlify(text.encode("ascii", "ignore"))
    result = str(bytes_)
    result = result[2:][:-1]
    return result

class Distance_Sensor():
    def __init__(self):
        self.serial = UART(3, 9600, timeout=0)  # open serial port
        self.wait(1.5)

    def wait(self, time=1):
        sleep(int(time*1000))

    def write_command(self, hex_string):
        hex_string = hex_string.replace(" ", "")
        self.serial.write(hex_to_bytes(hex_string))
        #self.wait_for_command_to_be_executed()

    def set_adress(self):
        self.write_command("FA 04 01 80 81")
        self.wait(6)

    def set_range(self,meters):
        if meters == 5:
            self.write_command("FA 04 09 05 F4")
        elif meters == 10:
            self.write_command("FA 04 09 0A EF")
        elif meters == 30:
            self.write_command("FA 04 09 1E DB")
        elif meters == 50:
            self.write_command("FA 04 09 32 C7")
        elif meters == 80:
            self.write_command("FA 04 09 50 A9")

    def set_frequency(self, frequencey):
        if frequencey == 5:
            self.write_command("FA 04 0A 05 F3")
        elif frequencey == 10:
            self.write_command("FA 04 0A 0A EE")
        elif frequencey == 20:
            self.write_command("FA 04 0A 14 E4") 

    def set_resolution(self,resolution):
        if resolution == 1:
            self.write_command("FA 04 0C 01 F5")
        elif resolution == 0.1:
            self.write_command("FA 04 0C 02 F4")
    
    def start_form_top(self):
        self.write_command("FA 04 08 01 F9")

    def start_from_bottom(self):
        self.write_command("FA 04 08 00 FA")

    def open_POD(self):                           #POD = power on test
        self.write_command("FA 04 0D 01 F4")
    
    def close_POD(self):
        self.write_command("FA 04 0D 00 F5")

    def measure_once(self):
        self.write_command("80 06 02 78")

    def measure_times(self):
        self.write_command("80 06 03 77")

    def set_time_between_maesures(self):
        self.write_command("FA 04 05 01 FC")

    def load_cache(self):
        self.write_command("80 06 07 73")

    def open_laser(self):
        self.write_command("80 06 05 01 74")

    def close_laser(self):
        self.write_command("80 06 05 00 75")

    def shut_down(self):
        self.write_command("80 04 02 7A")

    def read_result(self):
        #80 06 82 "3X 3X 3X 2E 3X 3X 3X" CS
        #80 06 82 30 30 30 2E 33 36 33 9E
        try:
            while True:
                if self.serial.any():
                    a_byte = self.serial.read(1)
                    a_hex = bytes_to_hex(a_byte)
                    #print(a_hex)
                    if a_hex == "80":
                        a_byte = self.serial.read(1)
                        a_hex = bytes_to_hex(a_byte)
                        if a_hex == "06":
                            a_byte = self.serial.read(1)
                            a_hex = bytes_to_hex(a_byte)
                            if a_hex == "82":
                                bytes_ = self.serial.read(7)
                                #print(bytes_)
                                return float(bytes_.decode("ascii", "ignore"))
                else:
                    self.wait(0.1)
        except Exception as e:
            print(e)
            return None



distance_sensor = Distance_Sensor()

while(True):
    img = sensor.snapshot()         # Take a picture and return the image.

    distance_sensor.measure_once()
    print(distance_sensor.read_result())
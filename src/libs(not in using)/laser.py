
from pyb import UART
from time import sleep
from commom import *


class Distance_Sensor():
    def __init__(self):
        self.serial = UART(3, 9600, timeout=0)
        # UART(3): (TX, RX) = (P4, P5)
        self.wait(1.5)

    def wait(self, time=1):
        sleep(int(time*1000))

    def write_command(self, hex_string):
        hex_string = hex_string.replace(" ", "")
        self.serial.write(hex_to_bytes(hex_string))
        # self.wait_for_command_to_be_executed()

    def set_adress(self):
        self.write_command("FA 04 01 80 81")
        self.wait(1)

    def set_range(self, meters):
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

    def set_resolution(self, resolution):
        if resolution == 1:
            self.write_command("FA 04 0C 01 F5")
        elif resolution == 0.1:
            self.write_command("FA 04 0C 02 F4")

    def start_form_top(self):
        self.write_command("FA 04 08 01 F9")

    def start_from_bottom(self):
        self.write_command("FA 04 08 00 FA")

    def open_POD(self):  # POD = power on test
        self.write_command("FA 04 0D 01 F4")

    def close_POD(self):
        self.write_command("FA 04 0D 00 F5")

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
        # 80 06 82 "3X 3X 3X 2E 3X 3X 3X" CS
        # 80 06 82 30 30 30 2E 33 36 33 9E
        try:
            while True:
                if self.serial.any():
                    a_byte = self.serial.read(1)
                    a_hex = bytes_to_hex(a_byte)
                    # print(a_hex)
                    if a_hex == "80":
                        a_byte = self.serial.read(1)
                        a_hex = bytes_to_hex(a_byte)
                        if a_hex == "06":
                            a_byte = self.serial.read(1)
                            a_hex = bytes_to_hex(a_byte)
                            if a_hex == "82":
                                bytes_ = self.serial.read(7)
                                # print(bytes_)
                                return float(bytes_.decode("ascii", "ignore"))
                else:
                    self.wait(0.1)
        except Exception as e:
            print(e)
            return None

    def measure_once(self):
        self.write_command("80 06 02 78")

    def measure_multiple_times(self):
        self.write_command("80 06 03 77")



if __name__ == "__main__":
    distance_sensor = Distance_Sensor()

    while(True):
        distance_sensor.measure_once()
        print(distance_sensor.read_result())
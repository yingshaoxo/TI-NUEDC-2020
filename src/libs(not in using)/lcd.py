import utime
import pyb
from commom import *


class OpenSmart_LCD():
    def __init__(self):
        self.serial = pyb.UART(1, 115200, timeout=0)
        # UART(1): (TX, RX) = (P1, P0)

        self.color_table = {
            "black": "0000",
            "blue": "001F",
            "red": "F800",
            "green": "07E0",
            "cyan": "07FF",
            "magenta": "F81F",
            "yellow": "FFE0",
            "white": "FFFF",
        }

        self.wait(1.5)
        self.set_baud()
        self.set_blacklight(150)
        self.fill_screen(self.color_table["white"])

    def wait(self, second=1):
        utime.sleep_ms(int(time * 1000))

    def reset(self):
        self.write_command("7E0205EF")
        self.wait(6)

    def set_baud(self):
        baud_index = int_to_hex(4)
        self.write_command("7E0340{baud_index}EF".format(baud_index=baud_index))

    def read_feedback_signal(self):
        bytes_string = ""
        start = 0
        attempts = 6
        while attempts:
            attempts -= 1
            # print(attempts)
            if self.serial.any():
                a_byte = self.serial.read(1)
                byte_string = bytes_to_hex(a_byte)
                #print(f"read: {byte_string}")
                if byte_string == "7E":
                    start = 1
                if start == 1:
                    bytes_string += byte_string
                    if byte_string == "EF":
                        return bytes_to_hex
            else:
                self.wait(0.1)

    def wait_for_command_to_be_executed(self):
        if self.read_feedback_signal() == "7E036F6BEF":
            return True
        else:
            return False

    def write_command(self, hex_string):
        self.serial.write(hex_to_bytes(hex_string))
        self.wait_for_command_to_be_executed()

    def set_blacklight(self, brightness):
        brightness_hex = int_to_hex(brightness)
        self.write_command("7E0306{brightness_hex}EF".format(brightness_hex=brightness_hex))

    def fill_screen(self, color="white"):
        if color in self.color_table.keys():
            color = self.color_table[color]
        self.write_command("7E0420{color}EF".format(color=color))

    def draw_pixel(self, x, y, color="black"):
        if color in self.color_table.keys():
            color = self.color_table[color]
        x = int_to_hex(x, 4)
        y = int_to_hex(y, 4)
        self.write_command("7E0821{x}{y}{color}EF".format(x=x, y=y, color=color))

    def draw_line(self, x0, y0, x1, y1, color="black"):
        if color in self.color_table.keys():
            color = self.color_table[color]
        x0 = int_to_hex(x0, 4)
        y0 = int_to_hex(y0, 4)
        x1 = int_to_hex(x1, 4)
        y1 = int_to_hex(y1, 4)
        self.write_command("7E0C24{x0}{y0}{x1}{y1}{color}EF".format(x0=x0, y0=y0, x1=x1, y1=y1, color=color))

    def draw_rectangle(self, x, y, width, height, color="black"):
        if color in self.color_table.keys():
            color = self.color_table[color]
        x = int_to_hex(x, 4)
        y = int_to_hex(y, 4)
        width = int_to_hex(width, 4)
        height = int_to_hex(height, 4)
        self.write_command("7E0C26{x}{y}{width}{height}{color}EF".format(x=x, y=y, width=width, height=height, color=color))

    def write_string(self, x, y, text):
        # set cursor
        self.write_command("7E060100000000EF")

        # set Text color
        self.write_command("7E0402f800EF")

        # set text size
        self.write_command("7E030302EF")

        def chunkstring(string, length):
            return [string[0+i:length+i] for i in range(0, len(string), length)]

        for i in range(y*2):
            # new line
            self.write_command("7E0210EF")
            self.write_command("7E0210EF")

        text_list = chunkstring(text, 5)
        for _, text in enumerate(text_list):
            text = text_to_hex(text.ljust(5))
            self.write_command("7E0711{text}EF".format(text=text))


if __name__ == "__main__":
    lcd = OpenSmart_LCD()

    index = 0
    while(True):
        if index > len(lcd.color_table):
            index = 0
        lcd.fill_screen(lcd.color_table[index])
        lcd.wait(1)
        index += 1

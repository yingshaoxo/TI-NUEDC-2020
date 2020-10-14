import utime
import pyb
import ubinascii
import ujson

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
        utime.sleep_ms(int(second * 1000))

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

    with open("font_pixels.json", "r") as f:
        text = f.read()
    font_dict = ujson.loads(text)

    def print_text(y, x, string):
        W = 320
        H = 240
        fh = len(list(font_dict.values())[0])
        fw = len(list(font_dict.values())[0][0])
        m = 2
        rows = 4
        columns = W//(fw+m)
        start_y = H // rows * y
        start_x = (fw+m) * x
        real_y = start_y + y
        real_x = start_x + x
        for char_index, char in enumerate(string):
            if char in font_dict.keys():
                char_array = font_dict[char]
                for row_index, row in enumerate(char_array):
                    for column_index, value in enumerate(row):
                        if value == 1:
                            lcd.draw_pixel(real_x +  (fw+m)*char_index  + column_index, real_y + row_index)
    
    print_text(0, 0, "正方形")
    print_text(1, 0, "球")
    print_text(2, 0, "三角形")

    #while(True):
    #    for key, value in lcd.color_table.items():
    #        lcd.fill_screen(value)
    #        lcd.wait(1)
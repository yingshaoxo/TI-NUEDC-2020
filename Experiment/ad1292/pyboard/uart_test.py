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


class Chars(MyLCD):
    def __init__(self, color=BLACK, font=None, bgcolor=None, scale=1, **kwargs):
        super(Chars, self).__init__(**kwargs)
        self.fontColor = color
        if font is not None:
            import fonts
            self._gcCollect()
            font = fonts.importing(font)
            self._font = font
            self.font = font
            del(fonts)
        else:
            from exceptions import NoneTypeFont
            raise NoneTypeFont
        self.bgcolor = bgcolor if bgcolor is None else self._get_Npix_monoword(
            bgcolor)
        self._fontscale = scale

        self.fontscale = scale

    @staticmethod
    @micropython.asm_thumb
    def _asm_get_charpos(r0, r1, r2):
        mul(r0, r1)
        adc(r0, r2)

    @micropython.viper
    def _get_bgcolor(self, x, y):
        self._set_window(x, x, y, y)
        data = self._write_cmd(RAMRD, read=True)
        data = self._decode_spi_data(data)
        return data

    def _set_word_length(self, data):
        return bin(data)[3:] * self.fontscale

    def _fill_bicolor(self, data, x, y, width, height, scale=None):
        bgcolor = self._get_bgcolor(x, y) if not self.bgcolor else self.bgcolor
        color = self.fontColor
        self._set_window(x, x + (height * scale) - 1, y, y + (width * scale))
        bgpixel = bgcolor * scale
        pixel = self._get_Npix_monoword(color) * scale
        words = ''.join(map(self._set_word_length, data))
        self._gcCollect()
        words = bytes(words, 'ascii').replace(
            b'0', bgpixel).replace(b'1', pixel)
        self._write_data(words)
        self._graph_orientation()

    def printChar(self, char, x, y, scale=None):
        if scale is None:
            scale = self.fontscale
        font = self._font
        self.fontscale = scale = 5 if scale >= 5 else scale
        index = ord(char)
        height = font['height']
        try:
            chrwidth = len(font[index]) * scale
            data = font[index]
        except KeyError:
            data = None
            chrwidth = font['width'] * scale
        X = self.current_height - y - (height * scale) + scale
        Y = x
        self._char_orientation()
        self._gcCollect()
        if data is None:
            self._graph_orientation()
            self.drawRect(x, y, height, chrwidth,
                          self.fontColor, border=2 * scale)
        else:
            self._fill_bicolor(data, X, Y, chrwidth, height, scale=scale)

    def printLn(self, string, x, y, bc=False, scale=None, strlen=None):
        if scale is None:
            scale = self.fontscale
        # if typed string length higher than strlen, string printing in new line
        strlen = self.current_width - 10 if strlen is None else strlen
        font = self.font
        X, Y = x, y
        scale = 3 if scale > 3 else scale
        for line in string.split('\n'):
            for word in line.split(' '):
                lnword = len(word)
                outofd = x + lnword * \
                    (font['width'] - font['width'] // 3) * scale
                if outofd >= strlen:
                    x = X
                    y += (font['height'] + 2) * scale
                for i in range(lnword):
                    chrwidth = len(font[ord(word[i])])
                    self.printChar(word[i], x, y, scale=scale)
                    chpos = self._return_chpos(chrwidth, scale)
                    x += self._asm_get_charpos(chrwidth, chpos, 3)
                x += self._asm_get_charpos(font['width'] // 4, chpos, 3)
            x = X
            y += (font['height'] + 2) * scale


class TwoWindow():
    def __init__(self):
        self.LCD = MyLCD(portrait=False)
        self.chars = Chars(color=BLACK, font="Arial_14", portrait=False)

        self.width = 320
        self.height = 240//2

        self.upper_x = 0
        self.upper_x_values = []
        self.upper_y_values = []
        self.last_upper_x_and_y = []

        self.lower_x = 0
        self.lower_x_values = []
        self.lower_y_values = []
        self.last_lower_x_and_y = []

        self.upper_text_function = None

    def get_filtered_upper_value(self, x, y):
        self.upper_x_values.append(x)
        self.upper_y_values.append(y)
        self.upper_x_values = self.upper_x_values[-16:]
        self.upper_y_values = self.upper_y_values[-16:]
        return sum(self.upper_x_values)/16, sum(self.upper_y_values)/16
    
    def map(self, x, i_m, i_M, o_m, o_M):
        return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

    def draw_at_the_upper_window1(self, value):
        space = 10
        if value > space:
            y = 0
        elif value < -space:
            y = self.height // 2
        else:
            y = self.height // 2 // 2

        if len(self.last_upper_x_and_y):
            self.LCD.drawLine(
                self.last_upper_x_and_y[0], self.last_upper_x_and_y[1], self.upper_x, y, RED)
        self.last_upper_x_and_y = [self.upper_x, y]

        self.upper_x += 1
        if (self.upper_x > self.width-1):
            self.clear_upper_window()
            self.upper_x = 0
            self.last_upper_x_and_y = []

    def draw_at_the_upper_window(self, max_value, value):
        percentage = value / max_value
        y = percentage * self.height
        #y = self.map(value, -300, 300, 0, self.height//2)
        if value > 0:
            y = 0
        else:
            y = self.height // 2

        smooth_x, smooth_y = self.get_filtered_upper_value(self.upper_x, y)
        if len(self.last_upper_x_and_y) and len(self.upper_x_values) == 16:
            self.LCD.drawLine(
                self.last_upper_x_and_y[0], self.last_upper_x_and_y[1], smooth_x, smooth_y, RED)
        else:
            self.LCD.drawPixel(smooth_x, smooth_y, RED)
        self.last_upper_x_and_y = [smooth_x, smooth_y]

        self.upper_x += 1
        if (self.upper_x > self.width-1):
            self.clear_upper_window()
            self.upper_x = 0
            self.upper_x_values = []
            self.upper_y_values = []
            self.last_upper_x_and_y = []

            if self.upper_text_function:
                self.upper_text_function()
            else:
                self.chars.printLn(str(percentage), 250, 10)

    def draw_text_at_the_upper_window(self, function):
        self.upper_text_function = function
        function()

    def clear_upper_window(self):
        self.LCD.drawRect(0, 0, self.width, self.height,
                          WHITE, border=0, infill=WHITE)

    def clear_lower_window(self):
        self.LCD.drawRect(0, self.height, self.width,
                          self.height*2, WHITE, border=0, infill=WHITE)


twoWindow = TwoWindow()

# tx: x9
# rx: x10
ser = UART(1, 115200)                         # init with given baudrate
i = 0
while 1:
    i += 1
    if i > 5000:
        i = 0
    if ser.any():
        two_byte = ser.read(2)
        if str(ubinascii.hexlify(two_byte))[2:-1] == "0afa":
            the_bytes = two_byte + ser.read(12)
            ecg = unpack("h", the_bytes[5:7])
            s32DaqVals = unpack("i", the_bytes[7:11])
            heart_rate = unpack("B", the_bytes[11:12])
            #if heart_rate[0] != 0:
                #print(ecg, s32DaqVals, heart_rate)
            twoWindow.draw_at_the_upper_window1(ecg[0])
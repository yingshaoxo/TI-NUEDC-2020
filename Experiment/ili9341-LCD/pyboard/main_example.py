import micropython
from micropython import const
import os

from array import array
from gc import collect
from math import ceil, cos, radians, sin, trunc
from struct import pack, unpack
from time import sleep

from machine import SPI, Pin

# Color definitions.
#     RGB 16-bit Color (R:5-bit; G:6-bit; B:5-bit)
BLACK = (0,  0,  0)  # 0,   0,   0
NAVY = (0,  0,  15)  # 0,   0, 128
DARKGREEN = (0,  31, 0)  # 0, 128,   0
DARKCYAN = (0,  31, 15)  # 0, 128, 128
MAROON = (15, 0,  0)        # 128,   0,   0
PURPLE = (15, 0,  15)        # 128,   0, 128
OLIVE = (15, 31, 0)        # 128, 128,   0
LIGHTGREY = (23, 47, 23)        # 192, 192, 192
DARKGREY = (15, 31, 15)        # 128, 128, 128
BLUE = (0,  0,  31)  # 0,   0, 255
GREEN = (0,  63, 0)  # 0, 255,   0
CYAN = (0,  63, 31)  # 0, 255, 255
RED = (31, 0,  0)        # 255,   0,   0
MAGENTA = (31, 0,  31)        # 255,   0, 255
YELLOW = (31, 63, 0)        # 255, 255,   0
WHITE = (31, 63, 31)        # 255, 255, 255
ORANGE = (31, 39, 0)        # 255, 165,   0
GREENYELLOW = (18, 63, 4)        # 173, 255,  47


# Constants

#   Miscelleanous
DEFAULT_BAUDRATE = const(42000000)
TFTWIDTH = 240       # TFT Width
TFTHEIGHT = 320       # TFT Height


#   IlI9341 registers definitions

# LCD control registers
NOP = const(0x00)
SWRESET = const(0x01)   # Software Reset

# LCD Read status registers
RDDID = const(0x04)   # Read Display Identification (24-Bit)
RDDST = const(0x09)   # Read Display Status (32-Bit)
RDDPM = const(0x0A)   # Read Display Power Mode (8-Bit)
RDDMADCTL = const(0x0B)   # Read Display MADCTL (8-Bit)
RDPIXFMT = const(0x0C)   # Read Display Pixel Format (8-Bit)
RDDIM = const(0x0D)   # Read Display Image Format (3-Bit)
RDDSM = const(0x0E)   # Read Display Signal Mode (8-Bit)
RDDSDR = const(0x0F)   # Read Display Self-Diagnostic Result (8-Bit)
RDID1 = const(0xDA)
RDID2 = const(0xDB)
RDID3 = const(0xDC)
RDID4 = const(0xDD)

# LCD settings registers
SLPIN = const(0x10)   # Enter Sleep Mode
SLPOUT = const(0x11)   # Exit Sleep Mode

PTLON = const(0x12)   # Partial Mode ON
NORON = const(0x13)   # Partial Mode OFF, Normal Display mode ON

INVOFF = const(0x20)
INVON = const(0x21)
GAMMASET = const(0x26)
LCDOFF = const(0x28)
LCDON = const(0x29)

CASET = const(0x2A)
PASET = const(0x2B)
RAMWR = const(0x2C)
RGBSET = const(0x2D)
RAMRD = const(0x2E)

PTLAR = const(0x30)
MADCTL = const(0x36)
PIXFMT = const(0x3A)   # Pixel Format Set

IFMODE = const(0xB0)   # RGB Interface Control
FRMCTR1 = const(0xB1)   # Frame Rate Control (In Normal Mode)
FRMCTR2 = const(0xB2)   # Frame Rate Control (In Idle Mode)
FRMCTR3 = const(0xB3)   # Frame Rate Control (In Partial Mode)
INVCTR = const(0xB4)   # Frame Inversion Control
PRCTR = const(0xB5)   # Blanking Porch ControlVFP, VBP, HFP, HBP
DFUNCTR = const(0xB6)
ETMOD = const(0xB7)   # Entry mode set

PWCTR1 = const(0xC0)
PWCTR2 = const(0xC1)
PWCTR3 = const(0xC2)
PWCTR4 = const(0xC3)
PWCTR5 = const(0xC4)
VMCTR1 = const(0xC5)
VMCTR2 = const(0xC7)

GMCTRP1 = const(0xE0)
GMCTRN1 = const(0xE1)
PWCTR6 = const(0xFC)
IFCTL = const(0xF6)

micropython.alloc_emergency_exception_buf(100)


class ILI(object):

    # def __init__(self, cs = '22', dc = '21', rst = None, bl = None,
    def __init__(self, cs='Y12', dc='Y11', rst='Y10', bl=None,
                 port=1, baud=DEFAULT_BAUDRATE, portrait=True):
        """ Initialize ILI class. """
        if cs is None or dc is None:
            raise RuntimeError('cs and dc pins must not be None')
        if port not in [1, 2]:
            raise RuntimeError('port must be HSPI or VSPI')

        self.csPin = Pin(cs, Pin.OUT)
        self.dcPin = Pin(dc, Pin.OUT)
        self.rstPin = None
        if rst is not None:
            self.rstPin = Pin(rst, Pin.OUT)
        self.blPin = None
        if bl is not None:
            self.blPin = Pin(bl, Pin.OUT)
            # Backlight On
            self.blPin.on()

        self.spi = SPI(port, baudrate=baud)
        self._portrait = portrait
        self.current_height = TFTHEIGHT
        self.current_width = TFTWIDTH

        self.reset()
        self._initILI()

        self._gcCollect()

    @micropython.viper
    def reset(self):
        """ Reset the Screen. """
        if self.rstPin:     # Reset Pin is Connected to ESP32
            self.rstPin.off()
            sleep(0.01)
            self.rstPin.on()
            return

    @micropython.viper
    def _gcCollect(self):
        collect()

    @micropython.viper
    def setDimensions(self):
        if self._portrait:
            self.current_height = TFTHEIGHT
            self.current_width = TFTWIDTH
        else:
            self.current_height = TFTWIDTH
            self.current_width = TFTHEIGHT
        self._graph_orientation()

    @micropython.viper
    def _initILI(self):
        self._write_cmd(LCDOFF)                     # Display OFF
        sleep(0.01)
        self._write_cmd(SWRESET)                    # Software Reset
        sleep(0.05)

        self._graph_orientation()  # set orientations

        self._write_cmd(PTLON)                      # Partial Mode ON
        self._write_cmd(PIXFMT)                     # Pixel Format Set
        # self._write_data(0x66)                     # 18-Bit/Pixel
        self._write_data(0x55)                      # 16-Bit/Pixel
        self._write_cmd(GAMMASET)
        self._write_data(0x01)
        self._write_cmd(ETMOD)                      # Entry Mode Set
        self._write_data(0x07)
        self._write_cmd(SLPOUT)                     # Exit Sleep Mode
        sleep(0.01)
        self._write_cmd(LCDON)                      # Display ON
        sleep(0.01)
        self._write_cmd(RAMWR)

    def _write(self, word, command=True, read=False):
        self.csPin.off()
        self.dcPin.value(0 if command else 1)
        if read:
            fmt = '>BI'
            data = bytearray(5)
            self.spi.write_readinto(pack(fmt, word), data)
            self.csPin.on()
            return data
        # self.spi.write(word)
        if isinstance(word, bytes):
            self.spi.write(bytearray(word))
        else:
            self.spi.write(bytearray([word]))
        self.csPin.on()

    def _decode_spi_data(self, data):
        # For example:
        #    1. recieving sets 5 bytes
        #    2. first 2 of them are useless (or null bytes)
        #    3. and just 3 last of them having a useful data:
        #        - those 3 bytes are RGB bytes (if we are reading from memory)
        #        - those 3 bytes have a 7 useful bits (and doesn't matter which color is)
        #        - we must get from them:
        #            * just 5 largest bits for R and B colors
        #            * just 6 largest bits for G color
        # next 2 lines sorting useful data
        # getting 4 last bytes
        data = unpack('<BI', data)[1]
        # reversing them
        data = pack('>I', data)
        # getting just 3 bytes from bytearray as BGR
        data = unpack('>3B', data)
        # with those 3 assignmentations we sorting useful bits for each color
        red = (((data[2] >> 2) & 31) << 11)
        green = (((data[1] >> 1) & 63) << 5)
        blue = ((data[0] >> 2) & 31)
        # setting them to 16 bit color
        data = red | green | blue
        data = pack('>H', data)
        return data

    def _write_cmd(self, word, read=False):
        data = self._write(word, read=read)
        return data

    def _write_data(self, word):
        self._write(word, command=False)

    def _write_words(self, words):
        wordL = len(words)
        wordL = wordL if wordL > 1 else ""
        fmt = '>{0}B'.format(wordL)
        words = pack(fmt, *words)
        self._write_data(words)

    @micropython.viper
    def _graph_orientation(self):
        self._write_cmd(MADCTL)   # Memory Access Control
        # Portrait:
        # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        # OR Landscape:
        # | MY=0 | MX=0 | MV=1 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        data = 0x48 if self._portrait else 0x28
        self._write_data(data)

    @micropython.viper
    def _char_orientation(self):
        self._write_cmd(MADCTL)   # Memory Access Control
        # Portrait:
        # | MY=1 | MX=1 | MV=1 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        # OR Landscape:
        # | MY=0 | MX=1 | MV=1 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        data = 0xE8 if self._portrait else 0x58
        self._write_data(data)

    @micropython.viper
    def _image_orientation(self):
        self._write_cmd(MADCTL)   # Memory Access Control
        # Portrait:
        # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        # OR Landscape:
        # | MY=0 | MX=1 | MV=0 | ML=1 | BGR=1 | MH=0 | 0 | 0 |
        data = 0xC8 if self._portrait else 0x68
        self._write_data(data)

    def _set_window(self, x0, y0, x1, y1):
        # Column Address Set
        self._write_cmd(CASET)
        self._write_words(((x0 >> 8) & 0xFF, x0 & 0xFF,
                           (y0 >> 8) & 0xFF, y0 & 0xFF))
        # Page Address Set
        self._write_cmd(PASET)
        self._write_words(((x1 >> 8) & 0xFF, x1 & 0xFF,
                           (y1 >> 8) & 0xFF, y1 & 0xFF))
        # Memory Write
        self._write_cmd(RAMWR)

    def _get_Npix_monoword(self, color):
        if color == WHITE:
            word = 0xFFFF
        elif color == BLACK:
            word = 0
        else:
            R, G, B = color
            word = (R << 11) | (G << 5) | B
        word = pack('>H', word)
        return word

    def _return_chpos(self, chrwidth, scale):
        if chrwidth == 1:
            chpos = scale + 1 if scale > 2 else scale - 1
        else:
            chpos = scale
        return chpos

    # Method written by MCHobby https://github.com/mchobby
    # Transform a RGB888 color to RGB565 color tuple.
    def rgbTo565(self, r, g, b):
        return (r >> 3, g >> 2, b >> 3)


class MyLCD(ILI):
    def __init__(self, cs='Y12', dc='Y11', rst='Y10', bl=None,
                 port=1, baud=DEFAULT_BAUDRATE, portrait=True):
        super().__init__(cs=cs, dc=dc, rst=rst, bl=bl,
                         port=port, baud=baud, portrait=portrait)
        self.setDimensions()
        self.fillScreen(WHITE)

    def _set_ortho_line(self, width, length, color):
        pixels = width * (length + 1)
        word = self._get_Npix_monoword(color) * pixels
        self._write_data(word)

    def drawPixel(self, x, y, color):
        x = int(x)
        y = int(y)
        self._set_window(x, x, y, y)
        self._write_data(self._get_Npix_monoword(color))

    def drawVline(self, x, y, length, color, width=1):
        if length > self.current_height:
            length = self.current_height
        if width > 10:
            width = 10
        self._set_window(x, x + (width - 1), y, y + length - 1)
        self._set_ortho_line(width, length, color)

    def drawHline(self, x, y, length, color, width=1):
        if length > self.current_width:
            length = self.current_width
        if width > 10:
            width = 10
        self._set_window(x, x + length - 1, y, y + (width - 1))
        self._set_ortho_line(width, length, color)

    def drawLine(self, x, y, x1, y1, color):
        if x == x1:
            self.drawVline(x, y if y <= y1 else y1, abs(y1 - y), color)
        elif y == y1:
            self.drawHline(x if x <= x1 else x1, y, abs(x-x1), color)
        else:
            # keep positive range for x
            if x1 < x:
                x, x1 = x1, x
                y, y1 = y1, y
            r = (y1 - y) / (x1 - x)
            # select ratio > 1 for fast drawing (and thin line)
            if abs(r) >= 1:
                for i in range(x1 - x + 1):
                    if (i == 0):  # always start at a point
                        self.drawPixel(x + i, trunc(y + (r * i)), color)
                    else:
                        # r may be negative when drawing the wrong way > Fix it when drawing
                        self.drawVline(x + i, trunc(y + (r * i) - r) +
                                       (0 if r > 0 else trunc(r)), abs(trunc(r)), color)
            else:
                # keep positive range for y
                if y1 < y:
                    x, x1 = x1, x
                    y, y1 = y1, y
                # invert the ratio (should be close of r = 1/r)
                r = (x1 - x) / (y1 - y)
                for i in range(y1 - y + 1):
                    if (i == 0):
                        self.drawPixel(trunc(x + (r * i)), y + i, color)
                    else:
                        # r may be negative when drawing the wrong way > fix it to draw positive
                        self.drawHline(
                            trunc(x + (r * i) - r) + (0 if r > 0 else trunc(r)), y + i, abs(trunc(r)), color)

    def drawRect(self, x, y, width, height, color, border=1, infill=None):
        if border is None:
            border = 0
        border = 10 if border > 10 else border
        if width > self.current_width:
            width = self.current_width
        if height > self.current_height:
            height = self.current_height
        height = 2 if height < 2 else height
        width = 2 if width < 2 else width
        self._graph_orientation()
        if border > 0:
            if border > width // 2:
                border = width // 2 - 1
            X, Y = x, y
            for i in range(2):
                Y = y + height - (border - 1) if i == 1 else y
                self.drawHline(X, Y, width, color, border)

                if border > 1:
                    Y = y + 1
                    H = height
                else:
                    Y = y
                    H = height + 1
                X = x + width - (border - 1) if i == 1 else x
                self.drawVline(X, Y, H, color, border)
        else:
            infill = color

        if infill:
            xsum = x + border
            ysum = y + border
            dborder = border * 2
            self._set_window(xsum, xsum + width - dborder,
                             ysum, ysum + height - dborder)
            # if MemoryError, try to set higher portion value
            portion = 32
            pixels = width * (height // portion + 1)
            pixels = pixels if height >= portion else (width * height) // 3 + 1
            times = 16 * 2 if height < portion + 1 else portion + 1
            self._gcCollect()
            word = self._get_Npix_monoword(infill) * pixels
            i = 0
            while i < (times):
                self._write_data(word)
                i += 1
        self._gcCollect()

    def fillMonocolor(self, color, margin=0):
        margin = 80 if margin > 80 else margin
        width = self.current_width - margin * 2
        height = self.current_height - margin * 2
        self.drawRect(margin, margin, width, height, color, border=0)

    def _get_x_perimeter_point(self, x, degrees, radius):
        sinus = sin(radians(degrees))
        x = trunc(x + (radius * sinus))
        return x

    def _get_y_perimeter_point(self, y, degrees, radius):
        cosinus = cos(radians(degrees))
        y = ceil(y - (radius * cosinus))
        return y

    def drawCircle(self, x, y, radius, color, border=1, degrees=360, startangle=0):
        border = 5 if border > 5 else border
        self._graph_orientation()
        # adding startangle to degrees
        if startangle > 0:
            degrees += startangle
        if border > 1:
            radius = radius-border // 2
        degp = 0.5
        quotient = int(divmod(1, degp)[0])
        for i in range(startangle, degrees):
            for j in tuple(i + degp * j for j in range(1, quotient + 1)):
                X = self._get_x_perimeter_point(x + degp, j, radius)
                Y = self._get_y_perimeter_point(y + degp, j, radius)
                self.drawHline(X, Y, border, color, border)

    def drawCircleFilled(self, x, y, radius, color):
        tempY = 0
        self._graph_orientation()
        for i in range(180):
            xNeg = self._get_x_perimeter_point(x, 360 - i, radius - 1)
            xPos = self._get_x_perimeter_point(x, i, radius)
            if i > 89:
                Y = self._get_y_perimeter_point(y, i, radius - 1)
            else:
                Y = self._get_y_perimeter_point(y, i, radius + 1)
            if i == 90:
                xPos = xPos - 1
            if tempY != Y and tempY > 0:
                length = xPos + 1
                self.drawHline(xNeg, Y, length - xNeg, color, width=4)
            tempY = Y

    def drawOvalFilled(self, x, y, xradius, yradius, color):
        tempY = 0
        self._graph_orientation()
        for i in range(180):
            xNeg = self._get_x_perimeter_point(x, 360 - i, xradius)
            xPos = self._get_x_perimeter_point(x, i, xradius)
            Y = self._get_y_perimeter_point(y, i, yradius)

            if i > 89:
                Y = Y - 1
            if tempY != Y and tempY > 0:
                length = xPos + 1
                self.drawHline(xNeg, Y, length - xNeg, color, width=4)
            tempY = Y

    def fillScreen(self, color):
        print(self.current_width)
        print(self.current_height)
        self.drawRect(0, 0, self.current_width, self.current_height,
                      color=color, border=0, infill=color)


def main():
    print("\n\n\n")
    print("start")

    myLCD = MyLCD(portrait=False)
    #bd.drawLine(0, 0, 240, 320, BLACK)
    myLCD.drawRect(10, 10, 30, 30, BLACK, border=1,
                   infill=myLCD.rgbTo565(255, 0, 255))

    width = 320
    height = 240
    x = 0.0
    y = 0.0
    while (1):
        x += 1
        if (x > 360):
            break
        y = sin(x*71/4068)
        actual_x = (x/360 * width)
        actual_y = ((y * height/2)+height/2)
        myLCD.drawPixel(actual_x, actual_y, BLACK)


if __name__ == '__main__':
    main()

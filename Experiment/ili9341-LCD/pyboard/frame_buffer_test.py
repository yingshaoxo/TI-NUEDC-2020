import framebuf
from machine import soft_reset, Pin, SPI
from time import sleep
from micropython import const
from struct import pack, unpack

Pin_SCK = "X6"
Pin_MISO = "X7"
Pin_MOSI = "X8"

Pin_DC = "Y11"
Pin_RST = "Y10"
Pin_CS = "Y12"


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


class LCDofYingshaoxo():
    def __init__(self, cs=Pin_CS, dc=Pin_DC, rst=Pin_RST, port=1, baud=42000000, portrait=False):
        self.width = 100
        self.height = 100

        self.buffer = bytearray(self.height*self.width*2)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)

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

        self.spi = SPI(port, baudrate=baud)
        self._portrait = portrait

        self.current_height = self.width
        self.current_width = self.height

        self.reset()
        self._initILI()

    def reset(self):
        """ Reset the Screen. """
        if self.rstPin:     # Reset Pin is Connected to ESP32
            self.rstPin.off()
            sleep(0.01)
            self.rstPin.on()
            return

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
        elif isinstance(word, bytearray):
            self.spi.write(word)
        else:
            self.spi.write(bytearray([word]))
        self.csPin.on()

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

    def _graph_orientation(self):
        self._write_cmd(MADCTL)   # Memory Access Control
        # Portrait:
        # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        # OR Landscape:
        # | MY=0 | MX=0 | MV=1 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        data = 0x48 if self._portrait else 0x28
        self._write_data(data)

    def _set_window(self, x0, y0, x1, y1):
        x0 = int(x0)
        y0 = int(y0)
        x1 = int(x1)
        y1 = int(y1)
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
    
    def draw_pixel(self):
        self._set_window(0, 100, 0, 100)
        self.framebuf.fill(0)
        self.framebuf.fill_rect(0, 0, self.width//2, self.height//2, 0xffff)
        self.framebuf.fill_rect(self.width//2, self.height//2, self.width, self.height , 0x4287)
        self._write_data(self.buffer)



def main():
    print("start")
    lcd = LCDofYingshaoxo()
    lcd.draw_pixel()
    print("done")


try:
    main()
except KeyboardInterrupt:
    import micropython
    import gc
    print("\nFree memory:\n", gc.mem_free())
    print("\n------\nMemory info:\n", micropython.mem_info())
    print("\n------\nStack usage:\n", micropython.stack_use())
    soft_reset()
#except Exception as e:
#    print(e)
#    soft_reset()
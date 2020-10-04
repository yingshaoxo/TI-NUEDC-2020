import utime
import random
from lcd_library import *


print("\n\n\n")
print("start")

width = 320
height = 240//2


LCD = MyLCD(portrait=False)
chars = Chars(color=BLACK, font="Arial_14", portrait=False)


def clear_window():
    LCD.drawRect(0, 0, width, height,
                 WHITE, border=0, infill=WHITE)


def get_a_number(min_value, max_value):
    return random.randint(min_value, max_value)


last_w = 0
last_h = 0
for w in range(width):
    for h in range(height):
        if (w % 10 == 0 and h % 10):
            LCD.drawLine(last_w, last_h, w, h, RED)
            last_w = w
            last_h = h


print("Done")

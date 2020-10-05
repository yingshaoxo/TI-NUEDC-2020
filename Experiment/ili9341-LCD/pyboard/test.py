import utime
import random
from lcd_library import *


def A():
    print("\nstart")

    width = 320
    height = 240//2

    LCD = MyLCD(portrait=False)

    def clear_window():
        LCD.drawRect(0, 0, width, height,
                     WHITE, border=0, infill=WHITE)

    def get_a_number(min_value, max_value):
        return random.randint(min_value, max_value)

    last_w = 0
    last_h = 0
    for w in range(width):
        for h in range(height):
            if (w % 20 == 0 and h % 20):
                LCD.drawLine(last_w, last_h, w, h, RED)
                last_w = w
                last_h = h

    print("Done")


def B():
    myLCD = MyLCD(portrait=False)

    width = 320
    height = 240 // 2

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

    width = 320
    height = 240 // 2

    x = 0.0
    y = 0.0
    while (1):
        x += 1
        if (x > 360):
            break
        y = sin(x*71/4068)
        actual_x = (x/360 * width)
        actual_y = ((y * height/2)+height/2)
        myLCD.drawPixel(actual_x, actual_y+height, BLACK)


def C():
    myLCD = MyLCD(portrait=False)
    myLCD.printLn("hi, yingshaoxo", 10, 10, scale=1)
    myLCD.printLn("hi, yingshaoxo", 320//2, 240//2, scale=3)

C()

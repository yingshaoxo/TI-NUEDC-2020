import utime
import random
from lcd_library import *


print("\n\n\n")
print("start")


class TwoWindow():
    def __init__(self):
        self.LCD = MyLCD(portrait=False)
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
    
    def get_filtered_upper_value(self, x, y):
        self.upper_x_values.append(x)
        self.upper_y_values.append(y)
        self.upper_x_values = self.upper_x_values[-16:]
        self.upper_y_values = self.upper_y_values[-16:]
        return sum(self.upper_x_values)/16, sum(self.upper_y_values)/16

    def draw_at_the_upper_window(self, max_value, value):
        percentage = value / max_value
        y = percentage * self.height

        smooth_x, smooth_y = self.get_filtered_upper_value(self.upper_x, y)
        if len(self.last_upper_x_and_y) and len(self.upper_x_values) == 16:
            self.LCD.drawLine(self.last_upper_x_and_y[0], self.last_upper_x_and_y[1], smooth_x, smooth_y, RED)
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

    def clear_upper_window(self):
        self.LCD.drawRect(0, 0, self.width, self.height,
                          WHITE, border=0, infill=WHITE)

    def clear_lower_window(self):
        self.LCD.drawRect(0, self.height, self.width,
                          self.height*2, WHITE, border=0, infill=WHITE)


def get_a_number(min_value, max_value):
    return random.randint(min_value, max_value)


twoWindow = TwoWindow()
past = utime.ticks_ms()
while ((utime.ticks_ms() - past) < 1000 * 3):
    value = get_a_number(0, 1024)
    twoWindow.draw_at_the_upper_window(1024, value)

print("OK")


import sensor, image, time

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 1000)     # Wait for settings take effect.


import pyb
from time import sleep

horizontal_servo = pyb.Servo(1)   # create a servo object on position P7
#vertical_servo = pyb.Servo(2)   # create a servo object on position P8
#horizontal_servo.speed(-100)
#vertical_servo.speed(-100)



while(True):
    img = sensor.snapshot()         # Take a picture and return the image.

    #horizontal_servo.angle(45)        # move servo 1 to 45 degrees
    #vertical_servo.angle(0)         # move servo 2 to 0 degrees

    horizontal_servo.angle(0)
    #vertical_servo.angle(90, 1500)

    sleep(4000)

    horizontal_servo.angle(-90) # right

    sleep(2000)
    
    horizontal_servo.angle(90) # left

    sleep(2000)
"""
    # move servo1 and servo2 synchronously, taking 1500ms
    horizontal_servo.angle(0, 1500)
    vertical_servo.angle(0, 1500)

    sleep(1000)
"""
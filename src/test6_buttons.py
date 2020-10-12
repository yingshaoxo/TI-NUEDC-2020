from pyb import Pin, ExtInt

BUTTON_STATE = 0

def Button1Callback(e):
    global BUTTON_STATE
    BUTTON_STATE = 1

def Button2Callback(e):
    global BUTTON_STATE
    BUTTON_STATE = 2

def Button3Callback(e):
    global BUTTON_STATE
    BUTTON_STATE = 3

ExtInt(Pin('P2'), ExtInt.IRQ_RISING, Pin.PULL_UP, Button1Callback)
ExtInt(Pin('P3'), ExtInt.IRQ_RISING, Pin.PULL_UP, Button2Callback)
ExtInt(Pin('P6'), ExtInt.IRQ_RISING, Pin.PULL_UP, Button3Callback)

while(True):
    print(BUTTON_STATE)
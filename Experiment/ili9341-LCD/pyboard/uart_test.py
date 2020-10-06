"""
We handle ad1292 here
"""


from lcd_library import *
enable()


print("\n")
print("Running...")


def hexlify(bytes_):
    return str(ubinascii.hexlify(bytes_))[2:-1]


class TwoWindow():
    def __init__(self):
        self.LCD = MyLCD(portrait=False, background=BLACK, char_color=WHITE)

        self.width = 320
        self.height = 240

        self.x = 0

        self.ecg_data = []
        self.ecg_window_skip = 2
        self.ecg_window_counting = 0
        self.last_y1 = 0

        self.resp_data = []
        self.resp_window_skip = 2
        self.resp_window_counting = 0
        self.resp_temp_min = 5000
        self.resp_temp_max = 6000
        self.resp_min = 5000
        self.resp_max = 6000

        self.bpm_value = 0
        self.resp_value = 0

        #self.LCD.drawVline(0,0,self.height, color=RED, width=1)

    def _map(self, x, i_m, i_M, o_m, o_M):
        return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

    def handle_ecg_data(self, value, kernel=1, range_val=5000):
        value = -value
        value = self._map(value, -range_val, range_val, 0, self.height)

        self.ecg_data.append(value)
        self.ecg_data = self.ecg_data[-kernel:]

        if (len(self.ecg_data) == kernel):
            self.x += 1
            if (self.x > 320):
                self.x = 0
                self.resp_min = (self.resp_min + self.resp_temp_min) // 2
                self.resp_max = (self.resp_max + self.resp_temp_max) // 2
                self.draw_bpm_and_resp_text()
                collect()

            self.ecg_data.sort()
            if len(self.ecg_data) > kernel // 2-1:
                return self.x, self.ecg_data[kernel//2-1]
            else:
                return self.x, value
        else:
            return None, None

    def draw_at_the_upper_window(self, value):
        id_ = "ecg"

        # for scaling the whole view, to see more waves
        self.ecg_window_counting += 1
        if self.ecg_window_counting < self.ecg_window_skip:
            return
        else:
            self.ecg_window_counting = 0

        # to get ride of noise by choice 2 from [-999, 2, 777]
        x, y = self.handle_ecg_data(value, kernel=3, range_val=5000)

        if (x and y):
            y //= 2
            self.clean_screen(x)
            # if (self.last_y1 != 0):
            self.LCD.drawLine(x-1, self.last_y1, x, y, RED)
            self.last_y1 = y

    def handle_resp_data(self, value, kernel=1):
        if value < self.resp_temp_min:
            self.resp_temp_min = value
        elif value > self.resp_temp_max:
            self.resp_temp_max = value

        value = self._map(value, self.resp_min, self.resp_max, 0, self.height)

        self.resp_data.append(value)
        self.resp_data = self.resp_data[-kernel:]
        if len(self .resp_data) == kernel:
            value = sum(self.resp_data) // kernel
            return value
        else:
            return None

    def draw_at_the_lower_window(self, value):
        id_ = "resp"

        # for scaling the whole view, to see more waves
        self.resp_window_counting += 1
        if (self.resp_window_counting < self.resp_window_skip):
            return
        else:
            self.resp_window_counting = 0

        # print(value)
        y = self.handle_resp_data(value, kernel=16)

        if y:
            self.LCD.drawPixel(self.x, y//2 + self.height//2, RED)
    
    def draw_bpm_and_resp_text(self):
        bpm = str(self.bpm_value)
        bpm += " "*(3-len(bpm))

        resp = str(self.resp_value)
        resp += " "*(2-len(resp))

        self.LCD.printLn("HR "+bpm, 250, 2, bc=BLACK)
        self.LCD.printLn("REPS "+resp, 250, 200, bc=BLACK)

    def clean_screen(self, x=None, y=0):
        if x == None:
            self.LCD.drawRect(0, 0, self.width, self.height, BLACK, border=0, infill=BLACK)
        else:
            if (x > 320 or x < 0):
                x = -1
            x += 1
            self.LCD.drawVline(x-1, y, self.height, BLACK, width=1)
            self.LCD.drawVline(x, y, self.height, BLACK, width=1)
            self.LCD.drawVline(x+1, y, self.height, BLACK, width=1)


# soft_reset()
alloc_emergency_exception_buf(100)

twoWindow = TwoWindow()

# tx: x9
# rx: x10
ser = UART(1, 115200, bits=8, parity=None, stop=1, flow=0, timeout=0, timeout_char=2, rxbuf=64)                         # init with given baudrate
i = 0
while 1:
    i += 1
    if i > 1000:
        i = 0

    if ser.any():
        try:
            heading1 = ser.read(1)
            if hexlify(heading1) == "0a":
                heading2 = ser.read(1)
                if hexlify(heading2) == "fa":
                    data_length_bytes = ser.read(2)
                    data_length = unpack("H", data_length_bytes)[0]
                    # print(data_length)
                    type_bytes = ser.read(1)
                    type_ = unpack("B", type_bytes)[0]
                    if type_ == 2:
                        data_bytes = ser.read(data_length)
                        data = unpack("<iiB", data_bytes)
                        ecg, resp, heart_rate = data
                        ecg //= 1000
                        resp %= 10000
                        # print(ecg, resp, heart_rate)
                        twoWindow.draw_at_the_upper_window(ecg)
                        twoWindow.draw_at_the_lower_window(resp)
                        twoWindow.bpm_value = heart_rate
                        twoWindow.resp_value = 0
        except KeyboardInterrupt:
            import micropython
            import gc
            print("\nFree memory:\n", gc.mem_free())
            print("\n------\nMemory info:\n", micropython.mem_info())
            print("\n------\nStack usage:\n", micropython.stack_use())
            soft_reset()
        except Exception as e:
            print(e)

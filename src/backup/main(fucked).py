import gc
import sensor
import image
from pyb import UART, Servo, Pin, ExtInt
from utime import sleep_ms
import time
import ubinascii
from pid import PID


#######################
# The servo
#######################
horizontal_servo = Servo(1)   # create a servo object on position P7
#vertical_servo = Servo(2)   # create a servo object on position P8
horizontal_servo.speed(-100)
vertical_servo.speed(-100)

horizontal_servo.angle(0)
vertical_servo.angle(10)


pan_pid = PID(p=0.07, i=0, imax=90)  # 脱机运行或者禁用图像传输，使用这个PID
tilt_pid = PID(p=0.05, i=0, imax=90)  # 脱机运行或者禁用图像传输，使用这个PID
"""
pan_pid = PID(p=0.1, i=0, imax=90)  # 在线调试使用这个PID
tilt_pid = PID(p=0.1, i=0, imax=90)  # 在线调试使用这个PID
"""

#######################
# The commom functions
#######################


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


#######################
# The Distance Sensor
#######################


class Distance_Sensor():
    def __init__(self):
        self.serial = UART(3, 9600, timeout=0)
        # UART(3): (TX, RX) = (P4, P5)
        self.wait(1.5)

    def wait(self, second=1):
        sleep_ms(int(second * 1000))

    def write_command(self, hex_string):
        hex_string = hex_string.replace(" ", "")
        self.serial.write(hex_to_bytes(hex_string))
        # self.wait_for_command_to_be_executed()

    def set_adress(self):
        self.write_command("FA 04 01 80 81")
        self.wait(1)

    def set_range(self, meters):
        if meters == 5:
            self.write_command("FA 04 09 05 F4")
        elif meters == 10:
            self.write_command("FA 04 09 0A EF")
        elif meters == 30:
            self.write_command("FA 04 09 1E DB")
        elif meters == 50:
            self.write_command("FA 04 09 32 C7")
        elif meters == 80:
            self.write_command("FA 04 09 50 A9")

    def set_frequency(self, frequencey):
        if frequencey == 5:
            self.write_command("FA 04 0A 05 F3")
        elif frequencey == 10:
            self.write_command("FA 04 0A 0A EE")
        elif frequencey == 20:
            self.write_command("FA 04 0A 14 E4")

    def set_resolution(self, resolution):
        if resolution == 1:
            self.write_command("FA 04 0C 01 F5")
        elif resolution == 0.1:
            self.write_command("FA 04 0C 02 F4")

    def start_form_top(self):
        self.write_command("FA 04 08 01 F9")

    def start_from_bottom(self):
        self.write_command("FA 04 08 00 FA")

    def open_POD(self):  # POD = power on test
        self.write_command("FA 04 0D 01 F4")

    def close_POD(self):
        self.write_command("FA 04 0D 00 F5")

    def set_time_between_maesures(self):
        self.write_command("FA 04 05 01 FC")

    def load_cache(self):
        self.write_command("80 06 07 73")

    def open_laser(self):
        self.write_command("80 06 05 01 74")

    def close_laser(self):
        self.write_command("80 06 05 00 75")

    def shut_down(self):
        self.write_command("80 04 02 7A")

    def read_result(self):
        # 80 06 82 "3X 3X 3X 2E 3X 3X 3X" CS
        # 80 06 82 30 30 30 2E 33 36 33 9E
        try:
            while True:
                if self.serial.any():
                    a_byte = self.serial.read(1)
                    a_hex = bytes_to_hex(a_byte)
                    # print(a_hex)
                    if a_hex == "80":
                        a_byte = self.serial.read(1)
                        a_hex = bytes_to_hex(a_byte)
                        if a_hex == "06":
                            a_byte = self.serial.read(1)
                            a_hex = bytes_to_hex(a_byte)
                            if a_hex == "82":
                                bytes_ = self.serial.read(7)
                                # print(bytes_)
                                return float(bytes_.decode("ascii", "ignore"))
                else:
                    self.wait(0.1)
        except Exception as e:
            print(e)
            return None

    def measure_once(self):
        self.write_command("80 06 02 78")

    def measure_multiple_times(self):
        self.write_command("80 06 03 77")


distance_sensor = Distance_Sensor()


#######################
# The LCD
#######################


class OpenSmart_LCD():
    def __init__(self):
        self.serial = UART(1, 115200, timeout=0)
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
        sleep_ms(int(second * 1000))

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
            text = text_to_hex("{:<5}".format(text))  # text.ljust(5)
            self.write_command("7E0711{text}EF".format(text=text))


lcd = OpenSmart_LCD()


#######################
# The camare
#######################


sensor.reset()
gc.enable()

# sensor.set_pixformat(sensor.RGB565)  # 灰度更快
sensor.set_pixformat(sensor.GRAYSCALE)  # 灰度更快
sensor.set_framesize(sensor.QVGA)  # 320 x 240
sensor.skip_frames(time=1000)


WIDTH = sensor.width()
HEIGHT = sensor.height()

"""
CROP_WIDTH = WIDTH
CROP_HEIGHT = HEIGHT
TOP_LEFT_X = WIDTH - CROP_WIDTH
TOP_LEFT_Y = HEIGHT - CROP_HEIGHT
BOTTOM_RIGHT_X = TOP_LEFT_X + CROP_WIDTH
BOTTOM_RIGHT_Y = TOP_LEFT_Y + CROP_HEIGHT
"""

TOP_LEFT_X = int(0 * WIDTH)
TOP_LEFT_Y = int(0 * HEIGHT)
CROP_WIDTH = int(1 * WIDTH)
CROP_HEIGHT = int(1 * HEIGHT)
BOTTOM_RIGHT_X = TOP_LEFT_X + CROP_WIDTH
BOTTOM_RIGHT_Y = TOP_LEFT_Y + CROP_HEIGHT


RED_THRESHOLD = (0, 100,   0, 127,   0, 127)  # L A B
GREEN_THRESHOLD = (0, 100,   -128, 0,   0, 127)  # L A B
BLUE_THRESHOLD = (0, 100,   -128, 127,   -128, 0)  # L A B


def find_max_blob(blobs):
    max_size = 0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob = blob
            max_size = blob[2]*blob[3]
    return max_blob


THRESHOLD = 100
EROSION_SIZE = 2


class MyEye():
    def __init__(self) -> None:
        self.img = None
        self.binary_img = None
        self.led_and_bee = Pin('P9', Pin.OUT_PP)
        self.led_and_bee.on()

    def update_img(self):
        self.img = sensor.snapshot().lens_corr(1.8)
        self.img = self.img.crop((TOP_LEFT_X, TOP_LEFT_Y, BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y), copy_to_fb=False)

    def get_shape_and_blob(self):
        counting_times = 10
        a = 0
        b = 0
        c = 0
        last_a = None
        last_b = None
        last_c = None
        for _ in range(counting_times):
            shape, blob = self.get_shape_and_blob_raw()
            if shape == "circle":
                a += 1
                last_a = blob
            if shape == "square":
                b += 1
                last_b = blob
            if shape == "triangle":
                c += 1
                last_c = blob
            last_blob = blob
        if a > b and a > c:
            return "circle", last_a
        elif b > a and b > c:
            return "square", last_b
        elif c > a and c > b:
            return "triangle", last_c
        return None, None

    def get_shape_and_blob_raw(self):
        white_board_area = CROP_HEIGHT * CROP_WIDTH
        gradient_descent = int(white_board_area * 0.1)

        threshold = white_board_area
        while threshold > 100:
            self.update_img()
            binary_img = self.img.binary([(0, THRESHOLD)], invert=True, copy=False)
            binary_img.erode(EROSION_SIZE)
            blobs = binary_img.find_blobs([RED_THRESHOLD, GREEN_THRESHOLD, BLUE_THRESHOLD], area_threshold=threshold)
            #blobs = self.img.find_blobs([(12, THRESHOLD)], area_threshold=threshold)
            if len(blobs):
                blob = find_max_blob(blobs)

                self.img.draw_cross(blob.cx(), blob.cy(), color=(255, 255, 255), thickness=3)
                self.img.draw_rectangle((blob.x(), blob.y(), blob.w(), blob.h()), color=(0, 0, 0), thickness=3)

                #print( "roundness: ", blob.roundness(), "     solidity: ", blob.solidity())
                solidity = blob.solidity()
                if (solidity > 0.9):
                    return "square", blob
                elif (0.78 < solidity < 0.9):
                    return "circle", blob
                elif (solidity < 0.78):
                    return "triangle", blob

            threshold -= gradient_descent

        return None, None

    def parse_blob(self, shape, blob):
        side_length = 0
        x = blob.cx() + TOP_LEFT_X
        y = blob.cy() + TOP_LEFT_Y
        perimeter = blob.perimeter()
        self.img.draw_rectangle(blob.rect(), color=(255, 255, 255))
        self.img.draw_cross(x, y, color=(0, 0, 0))

        if (shape == "triangle"):
            side_length = 0.8191146*perimeter // 3
        elif (shape == "square"):
            side_length = 0.7889620*perimeter // 4
        elif (shape == "circle"):
            side_length = 0.8849540*(blob.w() + blob.h()) // 2

        return shape, x, y, side_length

    def do_a_fixed_detection(self):
        self.update_img()
        shape, blob = self.get_shape_and_blob()
        if shape:
            shape, x, y, side_length = self.parse_blob(shape, blob)
            print("shape:", shape, "_____", "(x,y):", x, y, "_____", "side_length:", side_length)

            distance = None
            while distance == None:
                distance_sensor.measure_once()
                distance = distance_sensor.read_result()
            print("distance: ", distance)

            side_length = distance*side_length
            self.display_info(side_length, shape, distance)
            print("density: ", blob.density())
            print("solidity: ", blob.solidity())

            return True
        return False

    def display_info(self, side_length, shape, distance):
        side_length = str(side_length/10)
        distance = str(distance)
        lcd.fill_screen()
        if shape == "circle":
            lcd.write_string(0, 0, "diameter: " + side_length + " cm")
        else:
            lcd.write_string(0, 0, "side length: " + side_length + " cm")
        lcd.write_string(0, 1, "shape: " + shape)
        lcd.write_string(0, 2, "distance: " + distance + " m")
        print("shape:", shape, "_____", "side_length:", side_length, "_____", "distance:", distance)

    def find_white_box1(self):
        THRESHOLD = 100
        EROSION_SIZE = 2

        img = self.update_img()

        binary_img = img.binary([(0, THRESHOLD)], invert=True, copy=False)
        binary_img.erode(EROSION_SIZE)

        full_area = HEIGHT * WIDTH
        gradient_descent = int(full_area * 0.1)
        area_threshold = full_area
        while area_threshold > 100:
            blobs = binary_img.find_blobs([(25, 255)], area_threshold=area_threshold)
            if len(blobs):
                blob = find_max_blob(blobs)
                self.img.draw_cross(blob.cx(), blob.cy(), color=(0, 0, 0), size=10, thickness=2)
                self.img.draw_rectangle(blob.rect(), color=(255, 255, 255))
                return blob.x(), blob.y(), blob.w(), blob.h(), blob.cx(), blob.cy()
            area_threshold -= gradient_descent
        return 0, 0, WIDTH, HEIGHT, WIDTH//2, HEIGHT//2

    def find_white_box2(self):
        THRESHOLD = 100
        EROSION_SIZE = 2
        self.update_img()

        binary_img = self.img.copy().binary([(0, THRESHOLD)], invert=True, copy=False)
        binary_img.erode(EROSION_SIZE)

        gradient_descent_ratio = 0.05
        gh = int(HEIGHT * gradient_descent_ratio)  # gradient_descent_for_height
        gw = int(WIDTH * gradient_descent_ratio)  # gradient_descent_for_width
        mean_gate = int(255 * 0.6)

        top = 0
        left = 0
        right = 0
        bottom = 0
        try:
            for index in range(1//gradient_descent_ratio - 1):
                #print(top, left, right, bottom)
                count = 0
                # top
                mean = self.img.copy((left, top, WIDTH-right-left, gh)).get_statistics().mean()
                if mean <= mean_gate:
                    top = gh * (index+1)
                else:
                    count += 1
                # left
                mean = self.img.copy((left, top, gw, HEIGHT-bottom-top)).get_statistics().mean()
                if mean <= mean_gate:
                    left = gw * (index+1)
                else:
                    count += 1
                # right
                mean = self.img.copy((WIDTH-right-gw, top, gw, HEIGHT-bottom-top)).get_statistics().mean()
                if mean <= mean_gate:
                    right = gw * (index+1)
                else:
                    count += 1
                # bottom
                mean = self.img.copy((left, HEIGHT-bottom-gh, WIDTH-right-left, gh)).get_statistics().mean()
                if mean <= mean_gate:
                    bottom = gh * (index+1)
                else:
                    count += 1
                if count == 4:
                    break
        except Exception as e:
            # print(e)
            pass

        x = left
        y = top
        w = WIDTH-left-right
        h = HEIGHT-bottom-top
        if w == 0:
            w = WIDTH
        if h == 0:
            h = HEIGHT
        cx = w//2+left
        cy = h//2+top
        #self.img.draw_cross(cx, cy, color=(0, 0, 0), size=10, thickness=2)
        #self.img.draw_rectangle((left, top, w, h), color=(0, 0, 0))
        return left, top, w, h, cx, cy

    def find_white_box3(self):
        white_board_area = CROP_HEIGHT * CROP_WIDTH
        gradient_descent = int(white_board_area * 0.1)
        the_blob = None

        img = self.update_img()
        binary_img = self.img.binary([(0, THRESHOLD)], invert=True, copy=False)
        binary_img.erode(EROSION_SIZE)

        threshold = white_board_area
        while threshold > 100:
            blobs = binary_img.find_blobs([(0, THRESHOLD)], area_threshold=threshold)
            for blob in blobs:
                if (binary_img.invert().find_blobs([(0, THRESHOLD)], roi=blob.rect())):
                    the_blob = blob

            threshold -= gradient_descent

        blob = the_blob
        if the_blob:
            self.img.draw_cross(blob.cx(), blob.cy(), color=(0, 0, 0), size=10, thickness=2)
            self.img.draw_rectangle(blob.rect(), color=(255, 255, 255))
            return blob.x(), blob.y(), blob.w(), blob.h(), blob.cx(), blob.cy()
        return 0, 0, WIDTH, HEIGHT, WIDTH//2, HEIGHT//2

    def set_screen_cropping_args(self, x, y, w, h):
        global TOP_LEFT_X, TOP_LEFT_Y, CROP_WIDTH, CROP_HEIGHT, BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y
        TOP_LEFT_X += x
        TOP_LEFT_Y += y
        CROP_WIDTH = w
        CROP_HEIGHT = h
        BOTTOM_RIGHT_X = TOP_LEFT_X + CROP_WIDTH
        BOTTOM_RIGHT_Y = TOP_LEFT_Y + CROP_HEIGHT

    def update_crop_box_based_on_white_color(self):
        x, y, w, h, cx, cy = self.find_white_box2()
        self.set_screen_cropping_args(x, y, w, h)

    def tracking_a_point(self, x, y):
        TOP_LEFT_X = (WIDTH - CROP_WIDTH) // 2
        TOP_LEFT_Y = (HEIGHT - CROP_HEIGHT) // 2
        BOTTOM_RIGHT_X = TOP_LEFT_X + CROP_WIDTH
        BOTTOM_RIGHT_Y = TOP_LEFT_Y + CROP_HEIGHT

        screen_center_x = TOP_LEFT_X + CROP_WIDTH // 2
        screen_center_y = TOP_LEFT_Y + CROP_HEIGHT // 2

        pan_error = x-screen_center_x
        tilt_error = y-screen_center_y

        pan_output = pan_pid.get_pid(pan_error, 1) / 8
        tilt_output = tilt_pid.get_pid(tilt_error, 1) / 8

        horizontal_servo.angle(horizontal_servo.angle()+pan_output)
        vertical_servo.angle(vertical_servo.angle()-tilt_output)

    def tracking_an_object(self):
        self.update_img()
        shape, blob = self.get_shape_and_blob_raw()
        if shape:
            shape, x, y, side_length = self.parse_blob(shape, blob)
            self.tracking_a_point(x, y)
            return shape, x, y, side_length
        return None, None, None, None

    def reset_servo(self):
        horizontal_servo.angle(0)
        vertical_servo.angle(10)
        sleep_ms(1000)

    def tracking_white_board_by_using_distance_sensor(self, degree=30):
        self.reset_servo()

        left_min = degree
        right_max = -degree
        step = 3
        horizontal_servo.angle(left_min)
        i = left_min
        while True:
            self.update_img()
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                if 2 <= distance <= 3.1:
                    # horizontal_servo.angle(i+10)
                    break
                horizontal_servo.angle(i)
                sleep_ms(10)
                i -= step
            if i < right_max:
                break

    def tracking_white_board_by_using_distance_sensor2(self, degree=30):
        self.reset_servo()

        left_min = degree
        right_max = -degree
        step = 3
        horizontal_servo.angle(left_min)
        i = left_min
        while True:
            self.update_img()
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                if 2 <= distance <= 3.1:
                    now = distance
                    while True:
                        self.update_img()
                        distance_sensor.measure_once()
                        distance = distance_sensor.read_result()
                        if distance:
                            if now > distance:
                                return
                        i -= step
                        if i < right_max:
                            return
                horizontal_servo.angle(i)
                sleep_ms(10)
                i -= step
            if i < right_max:
                break

    def tracking_white_board_by_using_distance_sensor3(self):
        horizontal_servo.angle(30)
        step = 10
        a = 30
        dis = 3.1

        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance > 3.1:
                    a = a - step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break
            else:
                pass

        step = step*0.5

        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance < 3.1:

                    a = a + step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break

            else:
                pass
        step = step*0.5
        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance > 3.1:
                    a = a - step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break
        step = step*0.5

        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance < 3.1:

                    a = a + step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break

        step = step*0.5
        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance > 3.1:
                    a = a - step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break

        left = a + step*0.5

        step = 10
        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance > 3.1:
                    a = a + step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break
            else:
                pass

        step = step*0.5

        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance < 3.1:

                    a = a - step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break

            else:
                pass
        step = step*0.5
        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance > 3.1:
                    a = a + step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break
        step = step*0.5

        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance < 3.1:

                    a = a - step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break

        step = step*0.5
        while 1:
            distance_sensor.measure_once()
            distance = distance_sensor.read_result()
            if distance:
                # print(distance)
                if distance > 3.1:
                    a = a + step
                    horizontal_servo.angle(a)
                    time.sleep(500)
                else:
                    break
        right = a - 0.5*step
        distance_sensor.open_laser()

        b = (left+right)/2 + 1
        for i in range(2000):
            horizontal_servo.angle(b)

    def show_sound_and_light_once(self):
        self.led_and_bee.off()
        sleep_ms(1000)
        self.led_and_bee.on()
        sleep_ms(1000)

    def recognize_ball(self):
        """
        basketball: 篮球
        football: 足球
        volleyball: 排球
        """
        self.update_img()
        lcd.fill_screen()
        shape = None
        while shape == None:
            shape, blob = self.get_shape_and_blob()
            if shape:
                shape, x, y, side_length = self.parse_blob(shape, blob)

                print("density: ", blob.density())
                print("solidity: ", blob.solidity())

                solidity = blob.solidity()
                if solidity >= 0.7:
                    type_ = "basketball"
                elif 0.5 < solidity < 0.7:
                    type_ = "volleyball"
                elif solidity <= 0.5:
                    type_ = "football"
                
                distance = None
                while distance == None:
                    distance_sensor.measure_once()
                    distance = distance_sensor.read_result()
                print("distance: ", distance)

                lcd.write_string(0, 2, "distance: " + str(distance) + " m")
                lcd.write_string(0, 3, "type: " + type_)
                return True
        return False


#######################
# The buttons
#######################
BUTTON_STATE = 0
TASK_3 = False


def ResetButtonState():
    global BUTTON_STATE
    BUTTON_STATE = 0


def Button1Callback(e):
    global BUTTON_STATE
    sleep_ms(500)
    if (Pin('P2').value()):
        BUTTON_STATE = 1


def Button2Callback(e):
    global BUTTON_STATE, TASK_3
    sleep_ms(500)
    if (Pin('P6').value()):
        BUTTON_STATE = 2

def Button3Callback(e):
    global BUTTON_STATE, TASK_3
    sleep_ms(500)
    if (Pin('P8').value()):
        BUTTON_STATE = 3

ExtInt(Pin('P2'), ExtInt.IRQ_RISING, Pin.PULL_UP, Button1Callback)
ExtInt(Pin('P6'), ExtInt.IRQ_RISING, Pin.PULL_UP, Button2Callback)
ExtInt(Pin('P8'), ExtInt.IRQ_RISING, Pin.PULL_UP, Button3Callback)

#######################
# The task manager
#######################


class TaskManager():
    def __init__(self) -> None:
        self.myEye = MyEye()
        self.done = False
    
    def task1or2(self):
        distance_sensor.close_laser()
        print("task1or2 start...")
        #self.myEye.tracking_white_board_by_using_distance_sensor3()
        #print("white board tracing finished...")

        if self.myEye.do_a_fixed_detection():
            taskManager.done = True
            self.myEye.show_sound_and_light_once()
        print("task1or2 finished")

    def task3or4(self):
        distance_sensor.close_laser()
        print("task3or4 start...")

        if TASK_3:
            self.task3()
        else:
            self.task4()

        print("task3or4 finished")

    def task3(self):
        distance_sensor.close_laser()
        print("task3 start...")

        self.myEye.tracking_white_board_by_using_distance_sensor3()
        print("white board tracing finished...")

        #for _ in range(10):
        #    self.myEye.tracking_an_object()

        if self.myEye.do_a_fixed_detection():
            distance_sensor.open_laser()
            taskManager.done = True
            self.myEye.show_sound_and_light_once()

    def task4(self):
        distance_sensor.close_laser()
        print("task4 start...")

        self.myEye.tracking_white_board_by_using_distance_sensor3()
        print("white board tracing finished...")

        #for _ in range(10):
        #    self.myEye.tracking_an_object()

        if self.myEye.do_a_fixed_detection():
            distance_sensor.open_laser()

            self.myEye.recognize_ball()

            taskManager.done = True
            self.myEye.show_sound_and_light_once()



taskManager = TaskManager()
distance_sensor.open_laser()
taskManager.myEye.show_sound_and_light_once()
while 1:
    if BUTTON_STATE == 1:
        taskManager.task1or2()

    if BUTTON_STATE == 2:
        taskManager.task3()

    if BUTTON_STATE == 3:
        taskManager.task4()

    if (taskManager.done):
        ResetButtonState()
        taskManager.done = False
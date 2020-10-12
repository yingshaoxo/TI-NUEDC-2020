import gc
import sensor
import image
from pyb import UART, Servo, Pin, ExtInt
from utime import sleep_ms
import ubinascii
from pid import PID


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
TOP_LEFT_X = (WIDTH - CROP_WIDTH) // 2
TOP_LEFT_Y = (HEIGHT - CROP_HEIGHT) // 2
BOTTOM_RIGHT_X = TOP_LEFT_X + CROP_WIDTH
BOTTOM_RIGHT_Y = TOP_LEFT_Y + CROP_HEIGHT
"""
TOP_LEFT_X = int(0.25 * WIDTH)
TOP_LEFT_Y = int(0.25 * HEIGHT)
CROP_WIDTH = int(0.15 * WIDTH)
CROP_HEIGHT = int(0.15 * HEIGHT)
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
            if shape == "rectangle":
                b += 1
                last_b = blob
            if shape == "triangle":
                c += 1
                last_c = blob
            last_blob = blob
        if a > b and a > c:
            return "circle", last_a
        elif b > a and b > c:
            return "rectangle", last_b
        elif c > a and c > b:
            return "triangle", last_c
        return None, None
                
    def get_shape_and_blob_raw(self):
        self.update_img()

        white_board_area = CROP_HEIGHT * CROP_WIDTH
        gradient_descent = int(white_board_area * 0.1)

        threshold = white_board_area
        while threshold > 100:
            binary_img = self.img.binary([(0, THRESHOLD)], invert=True, copy=False)
            binary_img.erode(EROSION_SIZE)
            blobs = binary_img.find_blobs([RED_THRESHOLD, GREEN_THRESHOLD, BLUE_THRESHOLD], area_threshold=threshold)
            #blobs = self.img.find_blobs([(12, THRESHOLD)], area_threshold=threshold)
            if len(blobs):
                blob = find_max_blob(blobs)

                self.img.draw_cross(blob.cx(), blob.cy(), color=(255, 255, 255), thickness=3)
                self.img.draw_rectangle((blob.x(), blob.y(), blob.w(), blob.h()), color=(0, 0, 0), thickness=3)

                print( "roundness: ", blob.roundness(), "     solidity: ", blob.solidity())
                solidity = blob.solidity()
                if (solidity > 0.9):
                    return "rectangle", blob
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
            side_length = perimeter // 3
        elif (shape == "rectangle"):
            side_length = perimeter // 4
        elif (shape == "circle"):
            side_length = (blob.w() + blob.h()) // 2

        return shape, x, y, side_length

    def do_a_fixed_detection(self):
        self.update_img()
        shape, blob = self.get_shape_and_blob()
        if shape:
            shape, x, y, side_length = self.parse_blob(shape, blob)
            print("shape:", shape, "_____", "(x,y):", x, y, "_____", "side_length:", side_length)
            return True
        return False

    def display_info(self, side_length, shape, distance):
        side_length = str(side_length)
        distance = str(distance)
        lcd.fill_screen()
        lcd.write_string(0, 0, "side length: " + side_length)
        lcd.write_string(0, 1, "shape: " + shape)
        lcd.write_string(0, 2, "distance: " + distance)
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
        x, y, w, h, cx, cy = self.find_white_box3()
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
        shape, blob = self.get_shape_and_blob()
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

myEye = MyEye()
while 1:
    myEye.do_a_fixed_detection()
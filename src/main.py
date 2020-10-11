import sensor
import image
import gc
import time

sensor.reset()
gc.enable()

# sensor.set_pixformat(sensor.RGB565)  # 灰度更快
sensor.set_pixformat(sensor.GRAYSCALE)  # 灰度更快
sensor.set_framesize(sensor.QVGA)  # 320 x 240
sensor.skip_frames(time=1000)


CROP_WIDTH = 100
CROP_HEIGHT = 50
TOP_LEFT_X = (sensor.width() - CROP_WIDTH) // 2
TOP_LEFT_Y = (sensor.height() - CROP_HEIGHT) // 2
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


class MyEye():
    def __init__(self) -> None:
        self.img = None
        self.binary_img = None

    def update_img(self):
        gc.collect()
        self.img = sensor.snapshot().lens_corr(1.8).crop((TOP_LEFT_X, TOP_LEFT_Y, BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y), copy_to_fb=True)
        self.binary_img = self.img.copy().binary([RED_THRESHOLD, GREEN_THRESHOLD, BLUE_THRESHOLD])

    def release(self):
        self.update_img()

    """
    def get_shape_and_blob(self):
        temp_triangle_shape = None
        temp_triangle_blob = None
        for _ in range(10):
            shape, blob = self.get_shape_and_blob_raw()
            if shape == "circle":
                return shape, blob
            else:
                if shape == "rectangle":
                    return shape, blob
                elif shape == "triangle":
                    temp_triangle_shape = shape
                    temp_triangle_blob = blob
        return temp_triangle_shape, temp_triangle_blob
    """
    def get_shape_and_blob(self):
        shape_list = []
        last_blob = None
        accurate_shape = None
        for _ in range(10):
            shape, blob = self.get_shape_and_blob_raw()
            if shape:
                shape_list.append(shape)
                last_blob = blob
        if "circle" in shape_list: # if there has any circle, it's circle
            accurate_shape = "circle"
        elif "rectangle" in shape_list: # if there has any rectangle and no circle, it's rectangle 
            accurate_shape = "rectangle"
        elif "triangle" in shape_list: # if all of them are triangle, it's triangle
            accurate_shape = "triangle"
        return accurate_shape, last_blob

    def get_shape_and_blob_raw(self):
        TEST_TIMES = 5
        blob = None
        largest_line_num = 0
        for _ in range(TEST_TIMES):
            white_board_area = CROP_HEIGHT * CROP_WIDTH
            gradient_descent = int(white_board_area * 0.1)

            threshold = white_board_area
            while threshold > 100:
                blobs = self.img.find_blobs([RED_THRESHOLD, GREEN_THRESHOLD, BLUE_THRESHOLD], area_threshold=threshold)
                if len(blobs):
                    blob = find_max_blob(blobs)

                    sub_img = self.binary_img.copy(blob.rect())
                    line_count = 0
                    for l in sub_img.find_lines(threshold=5000):
                        line_count += 1
                    # print(line_count)
                    if line_count > largest_line_num:
                        largest_line_num = line_count

                    break

                threshold -= gradient_descent

        if largest_line_num == 3:
            return "triangle", blob
        elif largest_line_num == 4:
            return "rectangle", blob
        elif largest_line_num > 4:
            return "circle", blob
        else:
            return None, None

    def parse_blob(self, shape, blob):
        side_length = 0
        x = blob.cx()
        y = blob.cy()
        perimeter = blob.perimeter()
        self.img.draw_rectangle(blob.rect(), color=(255, 0, 0))
        self.img.draw_cross(x, y, color=(0, 255, 0))

        if (shape == "triangle"):
            side_length = perimeter // 3
        elif (shape == "rectangle"):
            side_length = perimeter // 4
        elif (shape == "circle"):
            side_length = (blob.w() + blob.h()) // 2

        return shape, x, y, side_length

    def do_a_fixed_detection(self):
        shape, blob = self.get_shape_and_blob()
        if shape:
            shape, x, y, side_length = self.parse_blob(shape, blob)
            print("shape:", shape, "_____", "(x,y):", x, y, "_____", "side_length:", side_length)
            return True
        return False


myEye = MyEye()

while 1:
    myEye.update_img()
    myEye.do_a_fixed_detection()

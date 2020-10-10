import sensor
import image
import gc
import time

gc.enable()

sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # 灰度更快
sensor.set_framesize(sensor.QQVGA)  # 640 x 480
sensor.skip_frames(time=1000)


WIDTH = sensor.width()
HEIGHT = sensor.height()


class MyEye():
    def __init__(self) -> None:
        self.img = None
    
    def get_the_white_board_tuple(self):
        tuple_ = self.find_rectangle(raw=True)
        if tuple_:
            return tuple_
        else:
            return None

    def get_shape_and_x_y(self, roi):
        x, y = self.find_circle(roi=roi)
        if x:
            return "circle", x, y

        x, y = self.find_rectangle(roi=roi)
        if x:
            return "rectangle", x, y

        return "triangle", 0, 0

    def update_img(self):
        # lens_corr(1.8)畸变矫正
        gc.collect()
        self.img = sensor.snapshot().lens_corr(1.8)

    def find_circle(self, roi=(0, 0, WIDTH, HEIGHT)):
        try:
            threshold = 3500
            while threshold > 1000:
                circle = None
                max_ = 0
                #for c in self.img.find_circles(roi, threshold=threshold, x_margin=10, y_margin=10, r_margin=10, r_min=2, r_max=100, r_step=2):
                for c in self.img.find_circles(roi, threshold=threshold):
                    if c.magnitude() > max_:
                        circle = c
                        max_ = c.magnitude()
                        break
                if circle != None:
                    self.img.draw_circle(circle.x(), circle.y(), circle.r(), color=(255, 0, 0))
                    x = circle.x()
                    y = circle.y()
                    r = circle.r()
                    self.img.draw_circle(x, y, 2, color=(0, 255, 0))
                    return x, y
                else:
                    threshold -= 200
            return None, None
        except Exception as e:
            print(e)
            return None, None

    def find_rectangle(self, roi=(0, 0, WIDTH, HEIGHT), raw=False):
        try:
            threshold = 20000
            while threshold > 10000:
                rect = None
                max_ = 0
                for r in self.img.find_rects(roi, threshold=threshold):
                    if r.magnitude() > max_:
                        rect = r
                        max_ = rect.magnitude()
                        break
                if rect != None:
                    self.img.draw_rectangle(rect.rect(), color=(255, 0, 0))
                    x = rect.x() + rect.w()//2
                    y = rect.y() + rect.h()//2
                    self.img.draw_circle(x, y, 2, color=(0, 255, 0))
                    if not raw:
                        return x, y
                    else:
                        return rect.rect()
                else:
                    threshold -= 1000
            return None, None
        except Exception as e:
            print(e)
            return None, None

    def release(self):
        self.update_img()


myEye = MyEye()

while 1:
    myEye.update_img()
    white_board = myEye.get_the_white_board_tuple()
    if white_board:
        shape, x, y = myEye.get_shape_and_x_y(roi=white_board)
        print(shape, x, y)

        myEye.release()
        break

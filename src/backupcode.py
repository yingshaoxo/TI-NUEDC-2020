import sensor
import image
import gc
import time

gc.enable()

sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # 灰度更快
sensor.set_framesize(sensor.QVGA)  # 320 x 240
sensor.skip_frames(time=1000)


CROP_WIDTH = 100
CROP_HEIGHT = 50
TOP_LEFT_X = (sensor.width() - CROP_WIDTH) // 2
TOP_LEFT_Y = (sensor.height() - CROP_HEIGHT) // 2
BOTTOM_RIGHT_X = TOP_LEFT_X + CROP_WIDTH
BOTTOM_RIGHT_Y = TOP_LEFT_Y + CROP_HEIGHT


class MyEye():
    def __init__(self) -> None:
        self.img = None

    def get_shape_and_x_y(self):
        try:
            # we assume each shape has different pixels
            threshold = 20000 
            while threshold > 1000:
                rectangles = self.img.find_blobs(threshold=threshold)
                if len(rectangles):
                    self.img.draw_rectangle(rectangles[0].rect(), color=(255, 0, 0))
                    x = rectangles[0].x() + rectangles[0].w()//2
                    y = rectangles[0].y() + rectangles[0].h()//2
                    self.img.draw_circle(x, y, 2, color=(0, 255, 0))
                    return "rectangle", x, y

                circles = self.img.find_circles(threshold=threshold)
                if len(circles):
                    self.img.draw_circle(circles[0].x(), circles[0].y(), circles[0].r(), color=(255, 0, 0))
                    x = circles[0].x()
                    y = circles[0].y()
                    r = circles[0].r()
                    self.img.draw_circle(x, y, 2, color=(0, 255, 0))
                    return "circle", x, y

                threshold -= 1000
            return None, None, None
        except Exception as e:
            print(e)
            return None, None, None

    def update_img(self):
        gc.collect()
        self.img = sensor.snapshot().lens_corr(1.8).crop((TOP_LEFT_X, TOP_LEFT_Y, BOTTOM_RIGHT_X, BOTTOM_RIGHT_Y), copy_to_fb=True)

    def find_circle(self):
        try:
            threshold = 3500
            while threshold > 1000:
                circle = None
                max_ = 0
                # for c in self.img.find_circles(roi, threshold=threshold, x_margin=10, y_margin=10, r_margin=10, r_min=2, r_max=100, r_step=2):
                for c in self.img.find_circles(threshold=threshold):
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

    def find_rectangle(self):
        try:
            threshold = 20000
            while threshold > 10000:
                rect = None
                max_ = 0
                for r in self.img.find_rects(threshold=threshold):
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

    shape, x, y = myEye.get_shape_and_x_y()
    print(shape, x, y)

    # myEye.release()
    # break


                        """
                        possibility_of_rectangle = blob.convexity()
                        possibility_of_circle = blob.roundness()
                        #print(possibility_of_rectangle, possibility_of_circle)
                        if (0.5<possibility_of_rectangle< 0.9 and possibility_of_circle < 0.9):
                            self.img.draw_rectangle(blob.rect(), color=(255, 0, 0))
                            x = blob.cx()
                            y = blob.cy()
                            self.img.draw_cross(x, y, color=(0, 255, 0))
                            return "rectangle", x, y
                        elif (possibility_of_rectangle == 1.0 and 0.9<possibility_of_circle < 0.95):
                            x = blob.cx()
                            y = blob.cy()
                            r = blob.w()//2
                            self.img.draw_circle(x, y, r, color=(255, 0, 0))
                            self.img.draw_cross(x, y, color=(0, 255, 0))
                            return "circle", x, y
                        elif (possibility_of_rectangle == 1.0 and possibility_of_circle > 0.95):
                            x = blob.cx()
                            y = blob.cy()
                            self.img.draw_rectangle(blob.rect(), color=(255, 0, 0))
                            self.img.draw_cross(x, y, color=(0, 255, 0))
                            return "triangle", x, y
                        """
import sensor
import image
import time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # 灰度更快
sensor.set_framesize(sensor.VGA) #640 x 480
sensor.skip_frames(time=2000)


WIDTH = sensor.width()
HEIGHT = sensor.height()
KERNEL = 4


class MyEye():
    def __init__(self) -> None:
        self.img = None

    def update_img(self):
        # lens_corr(1.8)畸变矫正
        self.img = sensor.snapshot().lens_corr(1.8)

    def find_circles(self, roi=(0, 0, WIDTH, HEIGHT), threshold=3500):
        # Circle对象有四个值: x, y, r (半径), 和 magnitude。
        # magnitude是检测圆的强度。越高越好

        # roi 是一个用以复制的矩形的感兴趣区域(x, y, w, h)。如果未指定，
        # ROI 即图像矩形。操作范围仅限于roi区域内的像素。

        # x_stride 是霍夫变换时需要跳过的x像素的数量。若已知圆较大，可增加
        # x_stride 。

        # y_stride 是霍夫变换时需要跳过的y像素的数量。若已知直线较大，可增加
        # y_stride 。

        # threshold 控制从霍夫变换中监测到的圆。只返回大于或等于阈值的圆。
        # 应用程序的阈值正确值取决于图像。注意：一条圆的大小是组成圆所有
        # 索贝尔滤波像素大小的总和。

        # x_margin 控制所检测的圆的合并。 圆像素为 x_margin 、 y_margin 和
        # r_margin的部分合并。

        # y_margin 控制所检测的圆的合并。 圆像素为 x_margin 、 y_margin 和
        # r_margin 的部分合并。

        # r_margin 控制所检测的圆的合并。 圆像素为 x_margin 、 y_margin 和
        # r_margin 的部分合并。

        # r_min，r_max和r_step控制测试圆的半径。
        # 缩小测试圆半径的数量可以大大提升性能。
        # threshold = 3500比较合适。如果视野中检测到的圆过多，请增大阈值；
        # 相反，如果视野中检测到的圆过少，请减少阈值。
        circles = []
        for c in self.img.find_circles(roi, threshold=threshold, x_margin=10, y_margin=10, r_margin=10, r_min=2, r_max=100, r_step=2):
            circles.append(c)
            self.img.draw_circle(c.x(), c.y(), c.r(), color=(255, 0, 0))
        circles.sort(key=lambda c: c.magnitude(), reverse=True)
        return circles

    def find_circle(self, roi=(0, 0, WIDTH, HEIGHT)):
        circles = self.find_circles(roi=roi)
        if len(circles):
            circle = circles[0]
            x = circle.x()
            y = circle.y()
            r = circle.r()
            self.img.draw_circle(x, y, 2, color=(0, 255, 0))
            return x, y, r
        else:
            return None, None, None

    def find_rectangles(self, roi=(0, 0, WIDTH, HEIGHT), threshold=10000):
        """
        return rectangles that was sorted by manitude, bigger one on top
        """
        rectangles = []
        for r in self.img.find_rects(roi, threshold=threshold):
            self.img.draw_rectangle(r.rect(), color=(255, 0, 0))
            rectangles.append(r)
        rectangles.sort(key=lambda r: r.magnitude(), reverse=True)
        return rectangles

    def find_rectangle(self, roi=(0, 0, WIDTH, HEIGHT)):
        rects = self.find_rectangles(roi=roi)
        if len(rects):
            rect = rects[0]
            x = rect.x() + rect.w()//2
            y = rect.y() + rect.h()//2
            self.img.draw_circle(x, y, 2, color=(0, 255, 0))
            return x, y
        else:
            return None, None


myEye = MyEye()
while 1:
    myEye.update_img()
    myEye.find_rectangle()
    myEye.find_circle()
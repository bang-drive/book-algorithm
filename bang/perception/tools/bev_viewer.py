from absl import app, flags
import cv2
import numpy as np

from bang.common.topic import Topic


flags.DEFINE_integer('dst_width', 512, 'Output image width.')
flags.DEFINE_integer('dst_height', 512, 'Output image height.')

# Bird's eye view trapezoid.
flags.DEFINE_integer('a', 512, 'Trapezoid a.')
flags.DEFINE_integer('h', 280, 'Trapezoid height.')
flags.DEFINE_float('slope', 0.1, 'Trapezoid slope.')

BLACK = (0, 0, 0)
ROAD_COLOR_LOWER_HSV = np.array([101, 3, 71])
ROAD_COLOR_UPPER_HSV = np.array([165, 46, 167])


class BEVTransformer(object):

    def __init__(self):
        trapezoid_a = flags.FLAGS.a
        trapezoid_h = flags.FLAGS.h
        slope_width = int(trapezoid_h / flags.FLAGS.slope)
        image_w = 1024
        image_h = 576

        self.padding = slope_width + trapezoid_a // 2 - image_w // 2
        image_w += 2 * self.padding

        # Bird's eye view trapezoid.
        top_left = (slope_width, image_h - trapezoid_h)
        top_right = (slope_width + trapezoid_a, image_h - trapezoid_h)
        bot_left = (0, image_h)
        bot_right = (image_w, image_h)

        # Warp the trapezoid to given width and height.
        src_vertice = np.float32([top_left, top_right, bot_right, bot_left])
        dst_vertice = np.float32([(0, 0), (flags.FLAGS.dst_width, 0),
                                  (flags.FLAGS.dst_width, flags.FLAGS.dst_height), (0, flags.FLAGS.dst_height)])
        self.M = cv2.getPerspectiveTransform(src_vertice, dst_vertice)

    @staticmethod
    def mark_road(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, ROAD_COLOR_LOWER_HSV, ROAD_COLOR_UPPER_HSV)
        # Remove noise.
        kernel = np.ones((20, 20), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # Smooth the mask.
        mask = cv2.GaussianBlur(mask, (9, 9), 0)
        image = cv2.bitwise_and(image, image, mask=mask)
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), mask

    def process(self, image):
        image = cv2.copyMakeBorder(image, 0, 0, self.padding, self.padding, cv2.BORDER_CONSTANT, value=BLACK)
        image = cv2.warpPerspective(image, self.M, (flags.FLAGS.dst_width, flags.FLAGS.dst_height))
        image, mask = self.mark_road(image)
        return image


def main(argv):
    bev = BEVTransformer()
    for message in Topic.subscribe(Topic.CAMERA):
        image = cv2.imdecode(np.frombuffer(message, dtype=np.uint8), cv2.IMREAD_COLOR)
        image = bev.process(image)
        cv2.imshow("Image", image)
        # Quit on ESC or 'q'.
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break


if __name__ == '__main__':
    app.run(main)

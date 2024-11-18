import os

from absl import app, flags
from ultralytics import YOLO
import cv2
import numpy as np

from bang.common.topic import Topic


flags.DEFINE_boolean('show', False, 'Show results.')

BLACK = (0, 0, 0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)

SRC_WIDTH = 1024
SRC_HEIGHT = 576
DST_WIDTH = 512
DST_HEIGHT = 512

BEV_A = 512
BEV_H = 280
BEV_SLOPE = 0.1
PADDING = int(BEV_H / BEV_SLOPE) + BEV_A // 2 - SRC_WIDTH // 2
OBSTABLE_SIZE = (20, 40)

ROAD_COLOR_LOWER_HSV = np.array([101, 3, 71])
ROAD_COLOR_UPPER_HSV = np.array([165, 46, 167])

MODEL = os.path.expanduser('~/.cache/yolo-models/yolo11x.pt')


class Perception(object):

    def __init__(self):
        # Bird's eye view trapezoid.
        slope_width = int(BEV_H / BEV_SLOPE)
        top_left = (slope_width, SRC_HEIGHT - BEV_H)
        top_right = (slope_width + BEV_A, SRC_HEIGHT - BEV_H)
        bot_left = (0, SRC_HEIGHT)
        bot_right = (SRC_WIDTH + 2 * PADDING, SRC_HEIGHT)

        # Warp the trapezoid to given width and height.
        src_vertice = np.float32([top_left, top_right, bot_right, bot_left])
        dst_vertice = np.float32([(0, 0), (DST_WIDTH, 0), (DST_WIDTH, DST_HEIGHT), (0, DST_HEIGHT)])
        self.M = cv2.getPerspectiveTransform(src_vertice, dst_vertice)

        self.yolo = YOLO(MODEL)

    def process(self, image):
        obstacles = self.detect_obstacles(image)
        image = self.wrap_bev(image)
        mask, image = self.mark_road(image)

        if flags.FLAGS.show:
            for x, y in obstacles:
                top_left = (x - OBSTABLE_SIZE[0] // 2, y - OBSTABLE_SIZE[1])
                bot_right = (x + OBSTABLE_SIZE[0] // 2, y)
                cv2.rectangle(image, top_left, bot_right, RED, -1)
            cv2.rectangle(image, (DST_WIDTH // 2 - 10, DST_HEIGHT - 20), (DST_WIDTH // 2 + 10, DST_HEIGHT), YELLOW, -1)
        for x, y in obstacles:
            mask[y, x] = 1
        return mask, image

    def xy2bev(self, x, y):
        point = np.array([x + PADDING, y, 1], dtype=np.float32)
        x, y, scale = np.matmul(self.M, point)
        return int(x / scale), int(y / scale)

    def detect_obstacles(self, image):
        obstacles = []
        for result in self.yolo(image, verbose=False):
            for box in result.boxes:
                xyxy = box.xyxy.cpu()[0]
                x, y = self.xy2bev((xyxy[0] + xyxy[2]) / 2, xyxy[3])
                if 0 <= x < DST_WIDTH and 0 <= y < DST_HEIGHT:
                    obstacles.append((x, y))
        return obstacles

    def wrap_bev(self, image):
        image = cv2.copyMakeBorder(image, 0, 0, PADDING, PADDING, cv2.BORDER_CONSTANT, value=BLACK)
        image = cv2.warpPerspective(image, self.M, (DST_WIDTH, DST_HEIGHT))
        return image

    @staticmethod
    def mark_road(image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, ROAD_COLOR_LOWER_HSV, ROAD_COLOR_UPPER_HSV)
        # Remove noise.
        kernel = np.ones((20, 20), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # Smooth the mask.
        mask = cv2.GaussianBlur(mask, (9, 9), 0)
        if flags.FLAGS.show:
            image[mask == 255] = GREEN
            image[mask != 255] = BLACK
        return mask, image


def main(argv):
    perception = Perception()
    for message in Topic.subscribe(Topic.CAMERA):
        image = cv2.imdecode(np.frombuffer(message, dtype=np.uint8), cv2.IMREAD_COLOR)
        # Mask off a rectangle at position (395, 520) and size (234, 56) which is the main car itself.
        image = cv2.rectangle(image, (395, 520), (395 + 234, 520 + 56), BLACK, -1)
        # Mark the upper half as black.
        image[:image.shape[0] // 2, :] = BLACK

        mask, image = perception.process(image)
        Topic.publish(Topic.PERCEPTION, {
            'data': mask.tolist(),
            'width': DST_WIDTH,
            'height': DST_HEIGHT,
        })
        if flags.FLAGS.show:
            cv2.imshow("Image", image)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break


if __name__ == '__main__':
    app.run(main)

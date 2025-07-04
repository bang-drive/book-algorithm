import os
import threading
import time

from absl import app, flags
from ultralytics import YOLO
import cv2
import numpy as np

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic


flags.DEFINE_boolean('show', False, 'Show results.')

FREQUENCY = 10
MODEL = os.path.expanduser('~/.cache/yolo-models/yolo11x.pt')
DESIRED_CLASSES = {'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck'}

BLACK = (0, 0, 0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
ROAD_COLOR_LOWER_HSV = np.array([101, 3, 71])
ROAD_COLOR_UPPER_HSV = np.array([165, 46, 167])

SRC_WIDTH = 1024
SRC_HEIGHT = 576
DST_WIDTH = 512
DST_HEIGHT = 512

BEV_A = 512
BEV_H = 280
BEV_SLOPE = 0.1
PADDING = int(BEV_H / BEV_SLOPE) + BEV_A // 2 - SRC_WIDTH // 2
OBSTABLE_SIZE = (20, 40)

# distance = pixel / scale. So the chasiss position and speed can be converted to pixel space or vice versa.
SCALE = 16.96


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
        self.message = None
        self.message_lock = threading.Lock()

    def message_receiver(self):
        for message in Topic.subscribe(Topic.CAMERA):
            with self.message_lock:
                self.message = message

    def parse_message(self):
        with self.message_lock:
            return cv2.imdecode(np.frombuffer(self.message, dtype=np.uint8), cv2.IMREAD_COLOR) if self.message else None

    def process(self):
        image = self.parse_message()
        if image is None:
            return
        # Mask off a rectangle at position (395, 520) and size (234, 56) which is the main car itself.
        image = cv2.rectangle(image, (395, 520), (395 + 234, 520 + 56), BLACK, -1)
        # Mark the upper half as black.
        image[:image.shape[0] // 2, :] = BLACK

        obstacles = self.detect_obstacles(image)
        image = self.wrap_bev(image)
        road_mask, ref_line = self.mark_road(image)
        Topic.publish(Topic.PERCEPTION, {
            'scale': SCALE,
            'time': time.time(),
            'road_mask': road_mask.tolist(),
            'reference_line': ref_line.tolist(),
            'obstacles': obstacles,
        })
        if flags.FLAGS.show:
            self.show(image, road_mask, ref_line, obstacles)

    def show(self, image, road_mask, ref_line, obstacles):
        image[road_mask == 255] = GREEN
        image[road_mask != 255] = BLACK
        cv2.rectangle(image, (DST_WIDTH // 2 - 10, DST_HEIGHT - 20), (DST_WIDTH // 2 + 10, DST_HEIGHT), YELLOW, -1)
        for x, y in obstacles:
            top_left = (int(x - OBSTABLE_SIZE[0] / 2), int(y - OBSTABLE_SIZE[1]))
            bot_right = (int(x + OBSTABLE_SIZE[0] / 2), int(y))
            cv2.rectangle(image, top_left, bot_right, RED, -1)

        if len(ref_line) > 0:
            p = np.polynomial.Polynomial(ref_line[::-1])
            for y1 in range(0, DST_HEIGHT - 10, 20):
                x1 = np.clip(int(p(y1)), 0, DST_WIDTH - 1)
                y2 = y1 + 10
                x2 = np.clip(int(p(y2)), 0, DST_WIDTH - 1)
                cv2.line(image, (x1, y1), (x2, y2), RED, 1)

        cv2.imshow('Perception', image)

    def xy2bev(self, x, y):
        point = np.array([x + PADDING, y, 1], dtype=np.float32)
        x, y, scale = np.matmul(self.M, point)
        return (x / scale, y / scale)

    def detect_obstacles(self, image):
        obstacles = []
        classes = self.yolo.names
        for result in self.yolo(image, verbose=False):
            for box in result.boxes:
                if classes[int(box.cls[0])] not in DESIRED_CLASSES:
                    continue
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
        return mask, Perception.calc_reference_line(mask)

    @staticmethod
    def calc_reference_line(road_mask):
        # Regression for reference line.
        X = []
        Y = []
        min_width = 100
        for y in range(0, 320, 16):
            left = 0
            right = DST_WIDTH - 1
            count = 0
            while left < right:
                while road_mask[y, left] != 255 and left < right:
                    left += 1
                while road_mask[y, right] != 255 and left < right:
                    right -= 1
                if left < right:
                    count += 2
                    left += 1
                    right -= 1
                elif road_mask[y, left] == 255:
                    count += 1
            if count >= min_width:
                X.append(left)
                Y.append(y)
        return np.polyfit(Y, X, 2) if len(X) > 2 else np.empty(0)

    def start(self):
        threading.Thread(target=self.message_receiver, daemon=True).start()
        timer = RecurringTimer(1.0 / FREQUENCY)
        while timer.wait():
            self.process()
            if flags.FLAGS.show:
                if (cv2.waitKey(1) & 0xFF) == ord('q'):
                    break


def main(argv):
    Perception().start()


if __name__ == '__main__':
    app.run(main)

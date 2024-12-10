import json
import threading

from absl import app, flags
import cv2
import numpy as np

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic


flags.DEFINE_boolean('show', False, 'Show results.')

FREQUENCY = 10
OBSTABLE_SIZE = (20, 40)
RED = (0, 0, 255)
PINK = (255, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)


class Prediction(object):

    def __init__(self):
        self.last_perception = None
        self.current_perception = None
        self.chasiss = None
        self.message_lock = threading.Lock()

    def message_receiver(self):
        for topic, message in Topic.subscribe([Topic.PERCEPTION, Topic.CHASSIS]):
            with self.message_lock:
                if topic == Topic.PERCEPTION:
                    self.last_perception = self.current_perception
                    self.current_perception = message
                else:
                    self.chasiss = message

    def parse_messages(self):
        with self.message_lock:
            if self.last_perception is None or self.chasiss is None:
                return None
            if not isinstance(self.last_perception, dict):
                self.last_perception = json.loads(self.last_perception)
            if not isinstance(self.current_perception, dict):
                self.current_perception = json.loads(self.current_perception)
            if not isinstance(self.chasiss, dict):
                self.chasiss = json.loads(self.chasiss)
            return self.last_perception.copy(), self.current_perception.copy(), self.chasiss.copy()

    def process(self):
        results = self.parse_messages()
        if results is None:
            return
        last_perception, current_perception, chasiss = results
        speed = self.estimate_others_speed(last_perception, current_perception, chasiss)
        obstacles = self.predict_n_seconds_later(0.5, current_perception, speed)
        Topic.publish(Topic.PREDICTION, {
            'obstacles': obstacles,
        })
        if flags.FLAGS.show:
            pred_obstacles = {(int(x), int(y)): (int(pred_x), int(pred_y)) for x, y, pred_x, pred_y in obstacles}
            image = np.zeros((current_perception['height'], current_perception['width'], 3), dtype=np.uint8)
            mask = np.array(current_perception['road_mask'])
            image[mask == 255] = GREEN
            image[mask != 255] = BLACK
            cv2.rectangle(image, (current_perception['width'] // 2 - 10, current_perception['height'] - 20),
                                 (current_perception['width'] // 2 + 10, current_perception['height']), YELLOW, -1)
            for x, y in current_perception['obstacles']:
                x, y = int(x), int(y)
                top_left = (int(x - OBSTABLE_SIZE[0] / 2), int(y - OBSTABLE_SIZE[1]))
                bot_right = (int(x + OBSTABLE_SIZE[0] / 2), int(y))
                cv2.rectangle(image, top_left, bot_right, RED, -1)
                if (pred_xy := pred_obstacles.get((x, y))) is not None:
                    x, y = pred_xy
                    top_left = (int(x - OBSTABLE_SIZE[0] / 2), int(y - OBSTABLE_SIZE[1]))
                    bot_right = (int(x + OBSTABLE_SIZE[0] / 2), int(y))
                    cv2.rectangle(image, top_left, bot_right, PINK, -1)
            if current_perception['reference_line']:
                p = np.polynomial.Polynomial(current_perception['reference_line'][::-1])
                for y1 in range(0, current_perception['height'] - 10, 20):
                    x1 = max(min(int(p(y1)), current_perception['width'] - 1), 0)
                    y2 = y1 + 10
                    x2 = max(min(int(p(y2)), current_perception['width'] - 1), 0)
                    cv2.line(image, (x1, y1), (x2, y2), RED, 1)
            cv2.imshow('Prediction', image)

    @staticmethod
    def estimate_others_speed(perception0, perception1, chasiss):
        adc_speed = np.linalg.norm((chasiss['speed']['x'], chasiss['speed']['z'])) * perception1['scale']
        if len(perception0['obstacles']) == 0 or len(perception1['obstacles']) == 0:
            return adc_speed
        t = perception1['time'] - perception0['time']

        adc_pos1 = (perception1['width'] / 2, perception1['height'])
        others_pos1 = (adc_pos1[0] + np.mean([pos[0] - adc_pos1[0] for pos in perception1['obstacles']]),
                       adc_pos1[1] + np.mean([pos[1] - adc_pos1[1] for pos in perception1['obstacles']]))
        adc_pos0 = (adc_pos1[0], adc_pos1[1] + adc_speed * t)
        others_pos0 = (adc_pos0[0] + np.mean([pos[0] - adc_pos0[0] for pos in perception0['obstacles']]),
                       adc_pos0[1] + np.mean([pos[1] - adc_pos0[1] for pos in perception0['obstacles']]))
        return np.linalg.norm((others_pos1[0] - others_pos0[0], others_pos1[1] - others_pos0[1])) / t

    def predict_n_seconds_later(self, n, perception, speed):
        ref_line = perception['reference_line']
        if not ref_line:
            return []

        obstacles = []
        for x, y in perception['obstacles']:
            heading = (2 * ref_line[0] * y + ref_line[1], -1)
            heading /= np.linalg.norm(heading)
            pred_x = x + heading[0] * speed * n
            if pred_x < 0 or pred_x >= perception['width']:
                continue
            pred_y = y + heading[1] * speed * n
            if pred_y < 0 or pred_y >= perception['height']:
                continue
            obstacles.append((x, y, pred_x, pred_y))
        return obstacles

    def start(self):
        threading.Thread(target=self.message_receiver).start()
        timer = RecurringTimer(1.0 / FREQUENCY)
        while timer.wait():
            self.process()
            if flags.FLAGS.show:
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord('q'):
                    break


def main(argv):
    Prediction().start()


if __name__ == '__main__':
    app.run(main)

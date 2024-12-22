import json
import threading
import warnings

from absl import app, flags
import cv2
import numpy as np

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic
from bang.control.control import Control
from bang.planning.cubic_planner import CubicPlanner


flags.DEFINE_boolean('show', False, 'Show results.')
flags.DEFINE_boolean('direct_control', False, 'Directly send control message.')

FREQUENCY = 10
OBSTABLE_SIZE = (20, 40)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)


class Planning(object):

    def __init__(self):
        self.perception = None
        self.chasiss = None
        self.prediction = None
        self.message_lock = threading.Lock()

    def message_receiver(self):
        for topic, message in Topic.subscribe([Topic.PERCEPTION, Topic.CHASSIS, Topic.PREDICTION]):
            with self.message_lock:
                if topic == Topic.PERCEPTION:
                    self.perception = message
                elif topic == Topic.CHASSIS:
                    self.chasiss = message
                elif topic == Topic.PREDICTION:
                    self.prediction = message

    def parse_messages(self):
        with self.message_lock:
            if self.perception is None or self.chasiss is None or self.prediction is None:
                return None
            if not isinstance(self.perception, dict):
                self.perception = json.loads(self.perception)
            if not isinstance(self.chasiss, dict):
                self.chasiss = json.loads(self.chasiss)
            if not isinstance(self.prediction, dict):
                self.prediction = json.loads(self.prediction)
            return self.perception.copy(), self.chasiss.copy(), self.prediction.copy()

    def process(self):
        messages = self.parse_messages()
        if messages is None:
            return
        perception, chasiss, prediction = messages
        road_mask = np.array(perception['road_mask'])
        height, width = road_mask.shape
        planner = CubicPlanner(road_mask)
        trajectory = planner.plan(perception, chasiss, prediction)
        result = {
            'source': 'cubic_planner',
            'trajectory': trajectory,
        }
        if flags.FLAGS.direct_control:
            Control.run_once(result)
        else:
            Topic.publish(Topic.PLANNING, result)

        if flags.FLAGS.show:
            # Draw road.
            image = np.zeros((height, width, 3), dtype=np.uint8)
            image[road_mask == 255] = GREEN
            image[road_mask != 255] = BLACK
            # Draw ADC.
            cv2.rectangle(image, (width // 2 - 10, height - 20), (width // 2 + 10, height), YELLOW, -1)
            # Draw perception obstacles.
            for x, y in perception['obstacles']:
                x, y = int(x), int(y)
                top_left = (int(x - OBSTABLE_SIZE[0] / 2), int(y - OBSTABLE_SIZE[1]))
                bot_right = (int(x + OBSTABLE_SIZE[0] / 2), int(y))
                cv2.rectangle(image, top_left, bot_right, RED, -1)
            # Draw trajectory.
            if trajectory:
                for i in range(0, len(trajectory) - 1, 2):
                    cv2.line(image, trajectory[i], trajectory[i + 1], RED, 1)
            cv2.imshow('Planning', image)

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
    # Disable RankWarning.
    warnings.filterwarnings('ignore')
    Planning().start()


if __name__ == '__main__':
    app.run(main)

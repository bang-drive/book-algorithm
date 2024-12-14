import json
import threading
import warnings

from absl import app, flags, logging
import cv2
import numpy as np

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic
from bang.planning.quintic_planner import QuinticPlanner


flags.DEFINE_boolean('show', False, 'Show results.')

FREQUENCY = 10
OBSTABLE_SIZE = (20, 40)
RED = (0, 0, 255)
PINK = (255, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
CONTROL_MAX = 32768
STEER_VALUES = {
    'LEFT': -CONTROL_MAX,
    'RIGHT': CONTROL_MAX,
    'STRAIGHT': 0,
}


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
        results = self.parse_messages()
        if results is None:
            return
        perception, chasiss, prediction = results
        road_mask = np.array(perception['road_mask'])
        height, width = road_mask.shape
        planner = QuinticPlanner(road_mask)
        trajectory_points = planner.plan(perception, chasiss, prediction)
        if len(trajectory_points) > 4:
            steer = int((trajectory_points[1][0] - width / 2) / 24 * CONTROL_MAX)
            steer = max(min(steer, CONTROL_MAX), -CONTROL_MAX)
            logging.info(steer)
            Topic.publish(Topic.CONTROL, {
                'source': 'quintic_planner',
                'steer': steer,
                'pedal': CONTROL_MAX,
            })

        if flags.FLAGS.show:
            # Draw road.
            image = np.zeros((height, width, 3), dtype=np.uint8)
            image[road_mask == 255] = GREEN
            image[road_mask != 255] = BLACK
            # Draw ADC.
            cv2.rectangle(image, (width // 2 - 10, height - 20), (width // 2 + 10, height), YELLOW, -1)
            # Draw perception obstacles.
            pred_obstacles = {(int(x), int(y)): (int(pred_x), int(pred_y))
                              for x, y, pred_x, pred_y in prediction['obstacles']}
            for x, y in perception['obstacles']:
                x, y = int(x), int(y)
                top_left = (int(x - OBSTABLE_SIZE[0] / 2), int(y - OBSTABLE_SIZE[1]))
                bot_right = (int(x + OBSTABLE_SIZE[0] / 2), int(y))
                cv2.rectangle(image, top_left, bot_right, RED, -1)
                # Draw predicted obstacles.
                if (pred_xy := pred_obstacles.get((x, y))) is not None:
                    x, y = pred_xy
                    top_left = (int(x - OBSTABLE_SIZE[0] / 2), int(y - OBSTABLE_SIZE[1]))
                    bot_right = (int(x + OBSTABLE_SIZE[0] / 2), int(y))
                    cv2.rectangle(image, top_left, bot_right, PINK, -1)
            # Draw trajectory.
            if trajectory_points:
                for i in range(0, len(trajectory_points) - 1, 2):
                    cv2.line(image, trajectory_points[i], trajectory_points[i + 1], RED, 1)
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

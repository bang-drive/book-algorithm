import json
import math
import threading

from absl import app
import numpy as np

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic


FREQUENCY = 10
PREDICTION_STEP = 0.1
PREDICTION_RANGE = 0.5


class Prediction(object):

    def __init__(self):
        self.prev_perception = None
        self.perception = None
        self.chasiss = None
        self.message_lock = threading.Lock()

    def message_receiver(self):
        for topic, message in Topic.subscribe([Topic.PERCEPTION, Topic.CHASSIS]):
            with self.message_lock:
                if topic == Topic.PERCEPTION:
                    self.prev_perception = self.perception
                    self.perception = message
                else:
                    self.chasiss = message

    def parse_messages(self):
        with self.message_lock:
            if self.prev_perception is None or self.chasiss is None:
                return None
            if not isinstance(self.prev_perception, dict):
                self.prev_perception = json.loads(self.prev_perception)
            if not isinstance(self.perception, dict):
                self.perception = json.loads(self.perception)
            if not isinstance(self.chasiss, dict):
                self.chasiss = json.loads(self.chasiss)
            return self.prev_perception.copy(), self.perception.copy(), self.chasiss.copy()

    def process(self):
        messages = self.parse_messages()
        if messages is None:
            return
        prev_perception, perception, chasiss = messages
        road_mask = np.array(perception['road_mask'])
        speed = self.estimate_speed(prev_perception, perception, chasiss['speed'])
        result = {
            'time_sequence': [],
            'obstacles': []
        }
        if (ref_line := perception['reference_line']) and (obstacles := perception['obstacles']):
            ref_line_derive = np.polyder(ref_line)
            now = perception['time']
            for t in np.arange(PREDICTION_STEP, PREDICTION_RANGE + PREDICTION_STEP / 2, PREDICTION_STEP):
                obstacles = self.predict(PREDICTION_STEP, road_mask, obstacles, speed, ref_line_derive)
                if len(obstacles) == 0:
                    break
                result['time_sequence'].append(now + t)
                result['obstacles'].append(obstacles)
        Topic.publish(Topic.PREDICTION, result)

    @staticmethod
    def estimate_speed(prev_perception, perception, speed):
        adc_speed = np.linalg.norm((speed['x'], speed['z'])) * perception['scale']
        if len(prev_perception['obstacles']) == 0 or len(perception['obstacles']) == 0:
            # Best guess as the adc speed.
            return adc_speed
        t = perception['time'] - prev_perception['time']

        pos = (np.mean([pos[0] for pos in perception['obstacles']]),
               np.mean([pos[1] for pos in perception['obstacles']]))
        prev_pos = (np.mean([pos[0] for pos in prev_perception['obstacles']]),
                    np.mean([pos[1] for pos in prev_perception['obstacles']]) + adc_speed * t)
        return math.dist(pos, prev_pos) / t

    def predict(self, t, road_mask, obstacles, speed, ref_line_derive):
        height, width = road_mask.shape
        obstacles = []
        for x, y in obstacles:
            heading = (-np.polyval(ref_line_derive, y), -1)
            heading /= np.linalg.norm(heading)
            pred_x = x + heading[0] * speed * t
            if pred_x < 0 or pred_x >= width:
                continue
            pred_y = y + heading[1] * speed * t
            if pred_y < 0 or pred_y >= height:
                continue
            obstacles.append((pred_x, pred_y))
        return obstacles

    def start(self):
        threading.Thread(target=self.message_receiver, daemon=True).start()
        timer = RecurringTimer(1.0 / FREQUENCY)
        while timer.wait():
            self.process()


def main(argv):
    Prediction().start()


if __name__ == '__main__':
    app.run(main)

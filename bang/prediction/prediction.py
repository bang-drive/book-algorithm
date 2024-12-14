import json
import threading

from absl import app
import numpy as np

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic


FREQUENCY = 10
PREDICTION_TIME = [0.1, 0.2, 0.3, 0.4, 0.5]


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
        results = self.parse_messages()
        if results is None:
            return
        prev_perception, perception, chasiss = results
        road_mask = np.array(perception['road_mask'])
        speed = self.estimate_others_speed(prev_perception, perception, chasiss, road_mask)
        prediction = {
            'time_sequence': [],
            'results': []
        }
        now = perception['time']
        for t in PREDICTION_TIME:
            prediction['time_sequence'].append(now + t)
            prediction['results'].append(self.predict_n_seconds_later(t, perception, speed, road_mask))
        Topic.publish(Topic.PREDICTION, prediction)

    @staticmethod
    def estimate_others_speed(prev_perception, perception, chasiss, road_mask):
        adc_speed = max(np.linalg.norm((chasiss['speed']['x'], chasiss['speed']['z'])) * perception['scale'], 100)
        if len(prev_perception['obstacles']) == 0 or len(perception['obstacles']) == 0:
            return adc_speed
        t = perception['time'] - prev_perception['time']

        height, width = road_mask.shape
        adc_pos1 = (width / 2, height)
        others_pos1 = (adc_pos1[0] + np.mean([pos[0] - adc_pos1[0] for pos in perception['obstacles']]),
                       adc_pos1[1] + np.mean([pos[1] - adc_pos1[1] for pos in perception['obstacles']]))
        adc_pos0 = (adc_pos1[0], adc_pos1[1] + adc_speed * t)
        others_pos0 = (adc_pos0[0] + np.mean([pos[0] - adc_pos0[0] for pos in prev_perception['obstacles']]),
                       adc_pos0[1] + np.mean([pos[1] - adc_pos0[1] for pos in prev_perception['obstacles']]))
        return np.linalg.norm((others_pos1[0] - others_pos0[0], others_pos1[1] - others_pos0[1])) / t

    def predict_n_seconds_later(self, n, perception, speed, road_mask):
        ref_line = perception['reference_line']
        if not ref_line:
            return []
        derive = np.polyder(ref_line)

        height, width = road_mask.shape
        obstacles = []
        for x, y in perception['obstacles']:
            heading = (np.polyval(derive, y), -1)
            heading /= np.linalg.norm(heading)
            pred_x = x + heading[0] * speed * n
            if pred_x < 0 or pred_x >= width:
                continue
            pred_y = y + heading[1] * speed * n
            if pred_y < 0 or pred_y >= height:
                continue
            obstacles.append((pred_x, pred_y))
        return obstacles

    def start(self):
        threading.Thread(target=self.message_receiver).start()
        timer = RecurringTimer(1.0 / FREQUENCY)
        while timer.wait():
            self.process()


def main(argv):
    Prediction().start()


if __name__ == '__main__':
    app.run(main)

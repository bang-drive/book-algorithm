import json
import math
import threading

from absl import app, flags
import numpy as np

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic


flags.DEFINE_boolean('show', False, 'Show results.')

PREDICTION_FREQUENCY = 10


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
        results = self.estimate_others(last_perception, current_perception, chasiss)
        if results is None:
            return
        heading, speed = results
        obstacles = self.predict_n_seconds_later(0.5, current_perception, heading, speed)
        Topic.publish(Topic.PREDICTION, {
            'obstacles': obstacles,
        })

    @staticmethod
    def estimate_others(perception0, perception1, chasiss):
        if len(perception0['obstacles']) == 0 or len(perception1['obstacles']) == 0:
            return None
        adc_speed = math.sqrt(chasiss['speed']['x'] ** 2 + chasiss['speed']['z'] ** 2) * perception1['scale']
        t = perception1['time'] - perception0['time']

        adc_pos1 = (perception1['width'] / 2, perception1['height'])
        others_pos1 = (adc_pos1[0] + np.mean([pos[0] - adc_pos1[0] for pos in perception1['obstacles']]),
                       adc_pos1[1] + np.mean([pos[1] - adc_pos1[1] for pos in perception1['obstacles']]))
        adc_pos0 = (adc_pos1[0], adc_pos1[1] + adc_speed * t)
        others_pos0 = (adc_pos0[0] + np.mean([pos[0] - adc_pos0[0] for pos in perception0['obstacles']]),
                       adc_pos0[1] + np.mean([pos[1] - adc_pos0[1] for pos in perception0['obstacles']]))

        heading = (others_pos1[0] - others_pos0[0], others_pos1[1] - others_pos0[1])
        heading_len = math.sqrt(heading[0] ** 2 + heading[1] ** 2)
        heading = (heading[0] / heading_len, heading[1] / heading_len)
        speed = math.sqrt((others_pos1[0] - others_pos0[0]) ** 2 + (others_pos1[1] - others_pos0[1]) ** 2) / t
        return heading, speed

    def predict_n_seconds_later(self, n, perception, heading, speed):
        obstacles = []
        for x, y in perception['obstacles']:
            x += heading[0] * speed * n
            if x < 0 or x >= perception['width']:
                continue
            y += heading[1] * speed * n
            if y < -perception['height'] / 2 or y >= perception['height']:
                continue
            obstacles.append((x, y))
        return obstacles

    def start(self):
        threading.Thread(target=self.message_receiver).start()
        timer = RecurringTimer(1.0 / PREDICTION_FREQUENCY)
        while timer.wait():
            self.process()


def main(argv):
    Prediction().start()


if __name__ == '__main__':
    app.run(main)

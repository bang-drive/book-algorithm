import json
import threading

from absl import app

from bang.common.timer import RecurringTimer
from bang.common.topic import Topic


FREQUENCY = 10
CONTROL_MAX = 32768
WIDTH = 512


class Control(object):

    def __init__(self):
        self.planning = None
        self.message_lock = threading.Lock()

    def message_receiver(self):
        for message in Topic.subscribe(Topic.PLANNING):
            with self.message_lock:
                self.planning = message

    def parse_messages(self):
        with self.message_lock:
            if self.planning is None:
                return None
            if not isinstance(self.planning, dict):
                self.planning = json.loads(self.planning)
            return self.planning.copy()

    def process(self):
        planning = self.parse_messages()
        if planning is None:
            return
        if control := self.planning_to_control(planning):
            Topic.publish(Topic.CONTROL, control)

    @staticmethod
    def planning_to_control(planning):
        trajectory = planning['trajectory']
        if len(trajectory) > 1:
            steer = int((trajectory[1][0] - WIDTH / 2) / 24 * CONTROL_MAX)
            steer = max(min(steer, CONTROL_MAX), -CONTROL_MAX)
            return {
                'source': planning['source'],
                'steer': steer,
                'pedal': CONTROL_MAX,
            }
        return None

    def start(self):
        threading.Thread(target=self.message_receiver).start()
        timer = RecurringTimer(1.0 / FREQUENCY)
        while timer.wait():
            self.process()


def main(argv):
    Control().start()


if __name__ == '__main__':
    app.run(main)

from datetime import datetime
import time

from absl import app, logging

from bang.common.topic import Topic


PUBLISH_INTERVAL = 0.1
SWITCH_SIDE_EVERY_N_SECONDS = 0.5


def main(argv):
    LEFT = -32768
    RIGHT = 32768

    steer = LEFT
    while True:
        ts = datetime.timestamp(datetime.now())
        if int(ts / SWITCH_SIDE_EVERY_N_SECONDS) % 2 == 0:
            if steer != LEFT:
                logging.info('Turnning left.')
            steer = LEFT
        else:
            if steer != RIGHT:
                logging.info('Turnning right.')
            steer = RIGHT
        Topic.publish(Topic.CONTROL, {'source', 'dragon_planner', 'steer': steer, 'pedal': 32768})
        time.sleep(PUBLISH_INTERVAL)


if __name__ == '__main__':
    try:
        app.run(main)
    except KeyboardInterrupt:
        pass

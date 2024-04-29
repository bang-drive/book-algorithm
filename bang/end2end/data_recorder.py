from absl import app, logging
import cv2
import numpy as np

from bang.common.topic import Topic


TOPIC = '/bang/camera'
LEFT = -32768
RIGHT = 32768


def main(argv):
    for message in Topic.subscribe(TOPIC):
        image = cv2.imdecode(np.frombuffer(message, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow("Image", image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        steer = 0
        if key == 81:
            logging.info('LEFT')
            steer = LEFT
        elif key == 83:
            logging.info('RIGHT')
            steer = RIGHT
        Topic.publish(Topic.CONTROL, {'steer': steer, 'pedal': 32768})


if __name__ == '__main__':
    app.run(main)

import os

from absl import app, flags
from ultralytics import YOLO
import cv2
import numpy as np

from bang.common.topic import Topic


flags.DEFINE_string('model', None, 'Yolo model path.')
flags.DEFINE_string('image', None, 'Image path for static detection, otherwise use live camera topic.')
flags.DEFINE_enum('task', 'auto', ['auto', 'seg', 'obb', 'track'], 'Prediction task type.')

GREEN = (0, 255, 0)
MODEL_SIZE = 'x'  # n, s, m, l, x


class YoloModel(object):
    def __init__(self):
        models_dir = os.path.join(os.path.dirname(__file__), '../models')
        if flags.FLAGS.task == 'auto' and flags.FLAGS.model is None:
            # All default.
            self.task = 'detect'
            self.yolo = YOLO(F'{models_dir}/yolo11{MODEL_SIZE}.pt')
        elif flags.FLAGS.task == 'auto':
            # Decide with specified model.
            if flags.FLAGS.model.endswith('seg.pt'):
                self.task = 'seg'
            elif flags.FLAGS.model.endswith('obb.pt'):
                self.task = 'obb'
            else:
                self.task = 'detect'
            self.yolo = YOLO(flags.FLAGS.model)
        elif flags.FLAGS.model is None:
            # Decide with specified task.
            self.task = flags.FLAGS.task
            if self.task == 'track':
                self.yolo = YOLO(F'{models_dir}/yolo11{MODEL_SIZE}.pt')
            else:
                self.yolo = YOLO(F'{models_dir}/yolo11{MODEL_SIZE}-{self.task}.pt')
        else:
            # All specified.
            self.task = flags.FLAGS.task
            self.yolo = YOLO(flags.FLAGS.model)

    def process(self, image):
        results = (self.yolo.predict(image, verbose=False) if self.task != 'track' else
                   self.yolo.track(image, verbose=False))
        return results[0].plot()


def main(argv):
    yolo = YoloModel()
    if flags.FLAGS.image is not None:
        image = cv2.imread(flags.FLAGS.image)
        image = yolo.process(image)
        cv2.imshow("Image", image)
        cv2.waitKey(0)
    else:
        for message in Topic.subscribe(Topic.CAMERA):
            image = cv2.imdecode(np.frombuffer(message, dtype=np.uint8), cv2.IMREAD_COLOR)
            image = yolo.process(image)
            cv2.imshow("Image", image)
            # Quit on ESC or 'q'.
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break


if __name__ == '__main__':
    app.run(main)

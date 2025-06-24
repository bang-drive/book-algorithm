from datetime import datetime
import os
import threading

from absl import app, flags, logging
from getkey import getkey, keys
import cv2
import numpy as np

from bang.common.topic import Topic


# Save camera shot to <data_dir>/YYMMDD_HHMMSS_MS.jpg
flags.DEFINE_string('data_dir', '.', 'Directory to save images.')

LAST_FRAME = None


def camera_receiver():
    global LAST_FRAME
    for message in Topic.subscribe(Topic.CAMERA):
        LAST_FRAME = message


def save_image():
    if LAST_FRAME is None:
        logging.error('No camera frame received.')
        return

    output_dir = flags.FLAGS.data_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    frame_id = datetime.now().strftime('%y%m%d_%H%M%S_%f')[:-3]
    output_file = os.path.abspath(os.path.join(output_dir, frame_id + '.jpg'))
    image = cv2.imdecode(np.frombuffer(LAST_FRAME, dtype=np.uint8), cv2.IMREAD_COLOR)
    cv2.imwrite(output_file, image)
    logging.info(F'Saved camera frame to {output_file}.')


def main(argv):
    threading.Thread(target=camera_receiver).start()

    while True:
        key = getkey()
        if key == keys.SPACE:
            save_image()


if __name__ == '__main__':
    app.run(main)

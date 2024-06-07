from datetime import datetime, timedelta
import json
import os
import pprint

from absl import app, flags
import cv2
import numpy as np

from bang.common.topic import Topic
from bang.end2end.common import count_subdir_files


# Save to <data_dir>/<label>/.../YYMMDD_HHMMSS_MS.jpg
flags.DEFINE_string('data_dir', None, 'Directory to save images.')
flags.mark_flag_as_required('data_dir')

flags.DEFINE_float('straight_saving_ratio', 0.3, 'The ratio of saving straight images.')
flags.DEFINE_float('left_saving_ratio', 1, 'The ratio of saving left turn images.')
flags.DEFINE_float('right_saving_ratio', 1, 'The ratio of saving right turn images.')


SPEED_THRESHOLD = 8  # The full range is 0-16
SAVE_INTERVAL = timedelta(seconds=0.3)

# Labels.
STRAIGHT = '0_STRAIGHT'
LEFT = '1_LEFT'
RIGHT = '2_RIGHT'


def main(argv):
    saved = count_subdir_files(flags.FLAGS.data_dir)
    pprint.pprint(saved)
    current_camera = None
    current_chassis = None
    last_save_time = datetime.now()
    for topic, message in Topic.subscribe([Topic.CAMERA, Topic.CONTROL, Topic.CHASSIS]):
        if topic == Topic.CAMERA:
            current_camera = message
            continue
        if topic == Topic.CHASSIS:
            current_chassis = message
            continue
        current_control = message
        if current_camera is None or current_chassis is None:
            continue

        # Check save interval.
        now = datetime.now()
        if last_save_time + SAVE_INTERVAL >= now:
            continue

        # Check speed.
        speed = json.loads(current_chassis).get('speed')
        speed_abs = np.sqrt(speed['x'] ** 2 + speed['y'] ** 2 + speed['z'] ** 2)
        if speed_abs < SPEED_THRESHOLD:
            continue

        # Get label.
        steer = json.loads(current_control)['steer']
        label = STRAIGHT
        dice = np.random.rand()
        if steer < 0:
            label = LEFT
            if dice > flags.FLAGS.left_saving_ratio:
                continue
        elif steer > 0:
            label = RIGHT
            if dice > flags.FLAGS.right_saving_ratio:
                continue
        else:
            if dice > flags.FLAGS.straight_saving_ratio:
                continue
        saved[label] += 1

        # Save image.
        output_dir = os.path.join(flags.FLAGS.data_dir, label, now.strftime('%y%m%d_%H'))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        last_save_time = now
        frame_id = now.strftime('%y%m%d_%H%M%S_%f')[:-3]
        image = cv2.imdecode(np.frombuffer(current_camera, dtype=np.uint8), cv2.IMREAD_COLOR)
        # Mask off a rectangle at position (395, 520) and size (234, 56) which is the main car
        # itself.
        image = cv2.rectangle(image, (395, 520), (395 + 234, 520 + 56), (0, 0, 0), -1)
        # Cut the image to the lower half.
        h, w = image.shape[:2]
        image = image[h // 2:, :]
        cv2.imwrite(F'{output_dir}/{frame_id}.jpg', image)

        pprint.pprint(saved)


if __name__ == '__main__':
    app.run(main)

from datetime import datetime, timedelta
import glob
import json
import os
import pprint

from absl import app, flags
import cv2
import numpy as np

from bang.common.topic import Topic


# Save to <data_dir>/<label>/.../YYMMDD_HHMMSS_MS.jpg
flags.DEFINE_string('data_dir', None, 'Directory to save images.')
flags.mark_flag_as_required('data_dir')


SPEED_THRESHOLD = 8  # The full range is 0-16
SAVE_INTERVAL = timedelta(seconds=0.3)

# Labels.
LEFT = 'LEFT'
RIGHT = 'RIGHT'
STRAIGHT = 'STRAIGHT'


def scan_saved():
    saved = {}
    for label in [LEFT, RIGHT, STRAIGHT]:
        data_dir = F'{flags.FLAGS.data_dir}/{label}'
        if os.path.exists(data_dir):
            saved[label] = len(glob.glob(F'{data_dir}/**/*.jpg', recursive=True))
        else:
            saved[label] = 0
    pprint.pprint(saved)
    return saved


def main(argv):
    saved = scan_saved()
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
        chassis = json.loads(current_chassis)
        speed = np.sqrt(chassis['speed']['x'] ** 2 + chassis['speed']['y'] ** 2 + chassis['speed']['z'] ** 2)
        if speed < SPEED_THRESHOLD:
            continue

        # Get label.
        steer = json.loads(current_control)['steer']
        label = STRAIGHT
        if steer < 0:
            label = LEFT
        elif steer > 0:
            label = RIGHT
        saved[label] += 1

        # Save image.
        output_dir = os.path.join(flags.FLAGS.data_dir, label, now.strftime('%y%m%d_%H'))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        last_save_time = now
        frame_id = now.strftime('%y%m%d_%H%M%S_%f')[:-3]
        image = cv2.imdecode(np.frombuffer(current_camera, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imwrite(F'{output_dir}/{frame_id}.jpg', image)

        pprint.pprint(saved)


if __name__ == '__main__':
    app.run(main)

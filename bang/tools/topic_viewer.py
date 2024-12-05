from curses import wrapper
import json
import os
import pprint

from absl import app, flags, logging
import cv2
import numpy as np

from bang.common.topic import Topic


flags.DEFINE_string('topic', None, 'Topic to view.')

LAST_SCREEN = None


def view_json(stdscr):
    global LAST_SCREEN
    for message in Topic.subscribe(flags.FLAGS.topic):
        data = json.loads(message)
        if flags.FLAGS.topic == Topic.PERCEPTION:
            data['data'] = '<mask>'

        stdscr.clear()
        LAST_SCREEN = pprint.pformat(data)
        stdscr.addstr(LAST_SCREEN)
        stdscr.refresh()


def view_image():
    for message in Topic.subscribe(flags.FLAGS.topic):
        image = cv2.imdecode(np.frombuffer(message, dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow("Image", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main(argv):
    target_topic = flags.FLAGS.topic
    if target_topic == Topic.CAMERA:
        logging.info(F'Viewing topic {target_topic} as IMAGE.')
        view_image()
    elif target_topic is not None:
        logging.info(F'Viewing topic {target_topic} as JSON.')
        try:
            wrapper(view_json)
        except KeyboardInterrupt:
            # Print the last screen before exit.
            global LAST_SCREEN
            print(LAST_SCREEN)


if __name__ == '__main__':
    if os.environ.get('TERMINFO') is None:
        term = os.environ.get('TERM', 'xterm-256color')
        for path in ['/usr/lib/terminfo', '/usr/share/terminfo']:
            terminfo = os.path.join(path, term[0], term)
            if os.path.exists(terminfo):
                os.environ['TERMINFO'] = path
                break
    app.run(main)

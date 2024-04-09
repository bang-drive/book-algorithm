from curses import wrapper
import json
import os
import pprint

from absl import app, flags, logging

from bang.common.topic import Topic


flags.DEFINE_string('topic', None, 'Topic to view.')

LAST_SCREEN = None


def view_json(stdscr):
    global LAST_SCREEN
    for message in Topic.subscribe(flags.FLAGS.topic):
        stdscr.clear()
        LAST_SCREEN = pprint.pformat(json.loads(message))
        stdscr.addstr(LAST_SCREEN)
        stdscr.refresh()


def main(argv):
    target_topic = flags.FLAGS.topic
    if target_topic == Topic.CAMERA:
        logging.info(F'Viewing topic {target_topic} as IMAGE.')
        # TODO(xiaoxq): Add image viewer.
    elif target_topic is not None:
        logging.info(F'Viewing topic {target_topic} as JSON.')
        try:
            wrapper(view_json)
        except KeyboardInterrupt:
            # Print the last screen before exit.
            global LAST_SCREEN
            print(LAST_SCREEN)


if __name__ == '__main__':
    if os.environ.get('TERMINFO') is None and os.path.exists('/usr/lib/terminfo'):
        os.environ['TERMINFO'] = '/usr/lib/terminfo'
    app.run(main)

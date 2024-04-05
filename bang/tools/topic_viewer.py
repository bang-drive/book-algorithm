from curses import wrapper
import pprint
import time

from absl import app, flags, logging

from bang.common.topic import Topic


flags.DEFINE_string('topic', None, 'Topic to view.')


def view_json(stdscr):
    for message in Topic.subscribe(flags.FLAGS.topic):
        stdscr.clear()
        stdscr.addstr(pprint.format(json.loads(data)))
        stdscr.refresh()


def main(argv):
    target_topic = flags.FLAGS.topic
    if target_topic == Topic.CAMERA:
        logging.info(F'Viewing topic {target_topic} as IMAGE.')
        # TODO(xiaoxq): Add image viewer.
    elif target_topic is not None:
        logging.info(F'Viewing topic {target_topic} as JSON.')
        wrapper(view_json)


if __name__ == '__main__':
    if os.environ.get('TERMINFO') is None and os.path.exists('/usr/lib/terminfo'):
        os.environ['TERMINFO'] = '/usr/lib/terminfo'
    app.run(main)

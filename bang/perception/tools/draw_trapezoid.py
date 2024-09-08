import os

from absl import app, flags, logging
import cv2


flags.DEFINE_string('input', None, 'Input image path.')
flags.mark_flag_as_required('input')
flags.DEFINE_string('output', None, 'Output image path.')
flags.mark_flag_as_required('output')

flags.DEFINE_integer('a', 512, 'Trapezoid a.')
flags.DEFINE_integer('h', 280, 'Trapezoid height.')
flags.DEFINE_float('slope', 0.1, 'Trapezoid slope.')

LINE_WIDTH = 2
BLACK = (0, 0, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)


def main(argv):
    trapezoid_a = flags.FLAGS.a
    trapezoid_h = flags.FLAGS.h
    slope_width = int(trapezoid_h / flags.FLAGS.slope)

    # Add padding to left and right.
    image = cv2.imread(flags.FLAGS.input)
    image_w = image.shape[1]
    padding = slope_width + trapezoid_a // 2 - image_w // 2
    image = cv2.copyMakeBorder(image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=BLACK)

    # Draw trapezoid.
    image_w, image_h = image.shape[1], image.shape[0]
    top_left = (slope_width, image_h - trapezoid_h)
    top_right = (slope_width + trapezoid_a, image_h - trapezoid_h)
    cv2.line(image, (0, image_h), top_left, RED, LINE_WIDTH)
    cv2.line(image, top_left, top_right, BLUE, LINE_WIDTH)
    cv2.line(image, top_right, (image_w, image_h), RED, LINE_WIDTH)

    output = os.path.abspath(flags.FLAGS.output)
    cv2.imwrite(output, image)
    logging.info(F'Saved image to {output}.')


if __name__ == '__main__':
    app.run(main)

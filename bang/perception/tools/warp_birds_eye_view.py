import os

from absl import app, flags, logging
import cv2
import numpy as np


flags.DEFINE_string('input', None, 'Input image path.')
flags.mark_flag_as_required('input')
flags.DEFINE_string('output', None, 'Output image path.')
flags.mark_flag_as_required('output')
flags.DEFINE_integer('dst_width', 512, 'Output image width.')
flags.DEFINE_integer('dst_height', 512, 'Output image height.')

# Bird's eye view trapezoid.
flags.DEFINE_integer('a', 512, 'Trapezoid a.')
flags.DEFINE_integer('h', 280, 'Trapezoid height.')
flags.DEFINE_float('slope', 0.1, 'Trapezoid slope.')

BLACK = (0, 0, 0)


def main(argv):
    trapezoid_a = flags.FLAGS.a
    trapezoid_h = flags.FLAGS.h
    slope_width = int(trapezoid_h / flags.FLAGS.slope)

    # Add padding to left and right.
    image = cv2.imread(flags.FLAGS.input)
    image_w = image.shape[1]
    padding = slope_width + trapezoid_a // 2 - image_w // 2
    image = cv2.copyMakeBorder(image, 0, 0, padding, padding, cv2.BORDER_CONSTANT, value=BLACK)

    # Bird's eye view trapezoid.
    image_w, image_h = image.shape[1], image.shape[0]
    top_left = (slope_width, image_h - trapezoid_h)
    top_right = (slope_width + trapezoid_a, image_h - trapezoid_h)
    bot_left = (0, image_h)
    bot_right = (image_w, image_h)

    # Warp the trapezoid to given width and height.
    src_vertice = np.float32([top_left, top_right, bot_right, bot_left])
    dst_vertice = np.float32([(0, 0), (flags.FLAGS.dst_width, 0),
                              (flags.FLAGS.dst_width, flags.FLAGS.dst_height), (0, flags.FLAGS.dst_height)])
    M = cv2.getPerspectiveTransform(src_vertice, dst_vertice)
    dst_image = cv2.warpPerspective(image, M, (flags.FLAGS.dst_width, flags.FLAGS.dst_height))

    output = os.path.abspath(flags.FLAGS.output)
    cv2.imwrite(output, dst_image)
    logging.info(F'Saved image to {output}.')


if __name__ == '__main__':
    app.run(main)

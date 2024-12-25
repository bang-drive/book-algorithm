import random
import time

from absl import app, flags
import cv2
import numpy as np

import bang.planning.conf as conf


flags.DEFINE_integer('n', 100, 'Random curves to draw.')

WIDTH = 512
HEIGHT = 512
BLACK = (0, 0, 0)
A_CANDIDATES = np.linspace(*conf.A_RANGE, conf.SLICE)
B_CANDIDATES = np.linspace(*conf.B_RANGE, conf.SLICE)


def generate_poly(a, b):
    x0, y0 = (WIDTH // 2, HEIGHT - 1)
    x1, y1 = (WIDTH // 2, 0)
    c = ((x0 - a * y0 ** 3 - b * y0 ** 2) - (x1 - a * y1 ** 3 - b * y1 ** 2)) / (y0 - y1)
    d = x0 - a * y0 ** 3 - b * y0 ** 2 - c * y0
    poly = np.polynomial.Polynomial([d, c, b, a])
    # Check if it goes too close or even out of the edge.
    for y in range(0, HEIGHT, conf.POINTS_SAMPLE_STEP):
        x = int(poly(y))
        if x < conf.SAFETY_BUFFER or x > WIDTH - conf.SAFETY_BUFFER:
            return None
    return poly


def main(argv):
    random.seed(time.time())
    # White background.
    image = np.ones((HEIGHT, WIDTH, 3), np.uint8) * 255
    i = 0
    while i < flags.FLAGS.n:
        a = random.choice(A_CANDIDATES)
        b = random.choice(B_CANDIDATES)
        poly = generate_poly(a, b)
        if poly is None:
            continue
        i += 1
        for y0 in range(0, HEIGHT - 1, 2):
            x0 = int(poly(y0))
            y1 = y0 + 1
            x1 = int(poly(y1))
            cv2.line(image, (x0, y0), (x1, y1), BLACK, 1)
    cv2.imshow('Cubic Splines', image)
    cv2.waitKey(0)


if __name__ == '__main__':
    app.run(main)

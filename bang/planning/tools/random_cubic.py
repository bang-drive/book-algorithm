import random
import time

from absl import app, flags, logging
import numpy as np

import bang.planning.conf as conf


flags.DEFINE_integer('n', 100000, 'Rounds to generate random polynomial curves.')

WIDTH = 512
HEIGHT = 512
X_CANDIDATES = list(range(conf.SAFETY_BUFFER, WIDTH - conf.SAFETY_BUFFER))


def generate_poly():
    point0 = (WIDTH // 2, HEIGHT - 1)
    point1 = random.choice(X_CANDIDATES), HEIGHT / 4 * 3
    point2 = random.choice(X_CANDIDATES), HEIGHT / 4 * 2
    point3 = random.choice(X_CANDIDATES), HEIGHT / 4
    X = [point0[0], point1[0], point2[0], point3[0]]
    Y = [point0[1], point1[1], point2[1], point3[1]]
    return np.polyfit(Y, X, 3)


def main(argv):
    random.seed(time.time())
    a = []
    b = []
    for _ in range(flags.FLAGS.n):
        poly = generate_poly()
        a.append(poly[0])
        b.append(poly[1])
    logging.info(F'a: 20%={np.percentile(a, 20):.6f}, 80%={np.percentile(a, 80):.6f}')
    logging.info(F'b: 20%={np.percentile(b, 20):.6f}, 80%={np.percentile(b, 80):.6f}')


if __name__ == '__main__':
    app.run(main)

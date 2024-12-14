import sys
import time

import numpy as np


SAFETY_BUFFER = 20
MIN_ROAD_WIDTH = 100
TRAJECTORY_SAMPLE_STEP = 32
A_RANGE = (-0.000025, 0.000025)
B_RANGE = (-0.025, 0.025)
SLICE = 50


class CubicPlanner(object):

    def __init__(self, road_mask):
        self.road_mask = road_mask
        height, width = road_mask.shape
        self.first_point = (width // 2, height - 1)
        self.last_point = (width // 2, 0)
        for y in range(0, height, 16):
            left = 0
            right = width - 1
            count = 0
            while left < right:
                while road_mask[y, left] != 255 and left < right:
                    left += 1
                while road_mask[y, right] != 255 and left < right:
                    right -= 1
                if left < right:
                    count += 2
                    left += 1
                    right -= 1
                elif road_mask[y, left] == 255:
                    count += 1
            if count >= MIN_ROAD_WIDTH:
                self.last_point = (left, y)
                break

    def plan(self, perception, chasiss, prediction):
        adc_speed = max(np.linalg.norm((chasiss['speed']['x'], chasiss['speed']['z'])) * perception['scale'], 100)
        best_trajectory = []
        best_trajectory_cost = sys.float_info.max
        for a in np.arange(*A_RANGE, (A_RANGE[1] - A_RANGE[0]) / SLICE):
            for b in np.arange(*B_RANGE, (B_RANGE[1] - B_RANGE[0]) / SLICE):
                trajectory, cost = self.generate_trajectory(a, b, adc_speed, prediction)
                if cost < best_trajectory_cost:
                    best_trajectory = trajectory
                    best_trajectory_cost = cost
        return best_trajectory

    def generate_trajectory(self, a, b, adc_speed, prediction):
        trajectory = []
        x1, y1 = self.first_point
        x2, y2 = self.last_point
        if x1 == x2:
            return trajectory, sys.float_info.max

        c = ((x1 - a * y1 ** 3 - b * y1 ** 2) - (x2 - a * y2 ** 3 - b * y2 ** 2)) / (y1 - y2)
        d = x1 - a * y1 ** 3 - b * y1 ** 2 - c * y1
        poly = np.polynomial.Polynomial([d, c, b, a])
        if not self.check_collision(poly, adc_speed, prediction):
            return trajectory, sys.float_info.max

        distance = 0
        height, width = self.road_mask.shape
        for y in range(self.first_point[1], self.last_point[1], -TRAJECTORY_SAMPLE_STEP):
            x = int(poly(y))
            left = x - SAFETY_BUFFER
            right = x + SAFETY_BUFFER
            if left < 0 or right >= width or not np.all(self.road_mask[y, left:right] == 255):
                return trajectory, sys.float_info.max
            if trajectory:
                distance += np.linalg.norm((x - trajectory[-1][0], y - trajectory[-1][1]))
            trajectory.append((x, y))
        # Use distance as cost.
        return trajectory, distance

    def check_collision(self, poly, adc_speed, prediction):
        now = time.time()
        for index, t in enumerate(prediction['time_sequence']):
            offset = t - now
            if offset <= 0:
                continue
            y0 = adc_speed * offset
            x0 = poly(y0)
            for x1, y1 in prediction['results'][index]:
                if np.linalg.norm((x1 - x0, y1 - y0)) < SAFETY_BUFFER:
                    return False
        return True

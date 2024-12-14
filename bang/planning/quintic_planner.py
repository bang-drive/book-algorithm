import sys

import numpy as np


OBSTABLE_SIZE = 40
MIN_ROAD_WIDTH = 100
TRAJECTORY_SAMPLE_STEP = 32
A_RANGE = (-0.000025, 0.000025)
B_RANGE = (-0.025, 0.025)
SLICE = 50


class QuinticPlanner(object):

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
        height, width = self.road_mask.shape
        adc_speed = max(np.linalg.norm((chasiss['speed']['x'], chasiss['speed']['z'])) * perception['scale'], 100)
        adc_pred_y = height - adc_speed * prediction['prediction_time']

        # Mark obstables on road_mask, (x,y) is the lower-middle point, and the size is (40, 40).
        for _, _, x, y in prediction['obstacles']:
            if y > adc_pred_y:
                top_left = (max(int(x - OBSTABLE_SIZE / 2), 0), max(int(y - OBSTABLE_SIZE), 0))
                bot_right = (min(int(x + OBSTABLE_SIZE / 2), width - 1), int(y))
                self.road_mask[top_left[1]:bot_right[1], top_left[0]:bot_right[0]] = 0

        best_trajectory = []
        best_trajectory_cost = sys.float_info.max
        for a in np.arange(*A_RANGE, (A_RANGE[1] - A_RANGE[0]) / SLICE):
            for b in np.arange(*B_RANGE, (B_RANGE[1] - B_RANGE[0]) / SLICE):
                trajectory, cost = self.generate_trajectory(a, b)
                if cost < best_trajectory_cost:
                    best_trajectory = trajectory
                    best_trajectory_cost = cost
        return best_trajectory

    def generate_trajectory(self, a, b):
        x1, y1 = self.first_point
        x2, y2 = self.last_point
        if x1 == x2:
            return [], sys.float_info.max
        c = ((x1 - a * y1 ** 3 - b * y1 ** 2) - (x2 - a * y2 ** 3 - b * y2 ** 2)) / (y1 - y2)
        d = x1 - a * y1 ** 3 - b * y1 ** 2 - c * y1
        p = np.polynomial.Polynomial([d, c, b, a])

        points = []
        distance = 0
        height, width = self.road_mask.shape
        for y in range(self.first_point[1], self.last_point[1], -TRAJECTORY_SAMPLE_STEP):
            x = int(p(y))
            # 1. On road and no hitting.
            if x < 0 or x >= width or self.road_mask[y, x] != 255:
                return points, sys.float_info.max
            if points:
                distance += np.linalg.norm((x - points[-1][0], y - points[-1][1]))
            points.append((x, y))
        return points, distance

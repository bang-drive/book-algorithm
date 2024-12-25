import math
import sys
import time

import numpy as np

import bang.planning.conf as conf


MIN_ROAD_WIDTH = 100


class CubicPlanner(object):

    def __init__(self, perception, chasiss, prediction):
        self.road_mask = np.array(perception['road_mask'])
        self.scale = perception['scale']
        self.speed = chasiss['speed']
        self.prediction = prediction

        height, width = self.road_mask.shape
        self.first_point = (width // 2, height - 1)
        self.last_point = (width // 2, 0)

        for y in range(0, height, conf.POINTS_SAMPLE_STEP):
            left = 0
            right = width - 1
            count = 0
            while left < right:
                while self.road_mask[y, left] != 255 and left < right:
                    left += 1
                while self.road_mask[y, right] != 255 and left < right:
                    right -= 1
                if left < right:
                    count += 2
                    left += 1
                    right -= 1
                elif self.road_mask[y, left] == 255:
                    count += 1
            if count >= MIN_ROAD_WIDTH:
                self.last_point = (left, y)
                break

    def plan(self):
        adc_speed = max(np.linalg.norm((self.speed['x'], self.speed['z'])) * self.scale, 100)
        best_trajectory = []
        best_trajectory_cost = sys.float_info.max
        for a in np.linspace(*conf.A_RANGE, conf.SLICE):
            for b in np.linspace(*conf.B_RANGE, conf.SLICE):
                trajectory, cost = self.generate_trajectory(a, b, adc_speed, best_trajectory_cost)
                if cost < best_trajectory_cost:
                    best_trajectory = trajectory
                    best_trajectory_cost = cost
        return best_trajectory

    def generate_trajectory(self, a, b, adc_speed, best_trajectory_cost):
        trajectory = []
        x0, y0 = self.first_point
        x1, y1 = self.last_point
        if x0 == x1:
            return trajectory, sys.float_info.max

        c = ((x0 - a * y0 ** 3 - b * y0 ** 2) - (x1 - a * y1 ** 3 - b * y1 ** 2)) / (y0 - y1)
        d = x0 - a * y0 ** 3 - b * y0 ** 2 - c * y0
        poly = np.polynomial.Polynomial([d, c, b, a])
        if self.has_collision(poly, adc_speed):
            return trajectory, sys.float_info.max

        distance = 0
        height, width = self.road_mask.shape
        for y in range(y0, y1, -conf.POINTS_SAMPLE_STEP):
            x = int(poly(y))
            left = x - conf.SAFETY_BUFFER
            right = x + conf.SAFETY_BUFFER
            if (left < 0 or right >= width or self.road_mask[y, left] != 255 or self.road_mask[y, right] != 255 or
                    self.road_mask[y, x] != 255):
                return trajectory, sys.float_info.max
            new_point = (x, y)
            if trajectory:
                distance += math.dist(new_point, trajectory[-1])
                if distance > best_trajectory_cost:
                    break
            trajectory.append(new_point)
        # Use distance as cost.
        return trajectory, distance

    def has_collision(self, poly, adc_speed):
        now = time.time()
        for index, t in enumerate(self.prediction['time_sequence']):
            offset = t - now
            if offset <= 0:
                continue
            y0 = adc_speed * offset
            x0 = poly(y0)
            for obstacle in self.prediction['obstacles'][index]:
                if math.dist((x0, y0), obstacle) < conf.SAFETY_BUFFER:
                    return True
        return False

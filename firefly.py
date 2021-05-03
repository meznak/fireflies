import configparser
import pygame as pg
from random import randint, uniform
from vehicle import Vehicle


class Firefly(Vehicle):

    def __init__(self):
        Firefly.set_boundary(Firefly.edge_distance_pct)

        # Randomize starting position and velocity
        start_position = pg.math.Vector2(
            uniform(0, Firefly.max_x),
            uniform(0, Firefly.max_y))
        start_velocity = pg.math.Vector2(
            uniform(-1, 1) * Firefly.max_speed,
            uniform(-1, 1) * Firefly.max_speed)

        super().__init__(start_position, start_velocity,
                         Firefly.min_speed, Firefly.max_speed,
                         Firefly.max_force, Firefly.can_wrap,
                         Firefly.color, Firefly.flash_color)

        self.rect = self.image.get_rect(center=self.position)
        self.flash_interval = randint(Firefly.min_interval,
                                      Firefly.max_interval)
        self.flash_length = randint(Firefly.min_flash, Firefly.max_flash)
        self.flash_cycle = 0
        self.is_flashing = False

        self.debug = Firefly.debug

    @staticmethod
    def config(config: dict):
        for key in config:
            if key in ['debug', 'can_wrap']:
                setattr(Firefly, key, config.getboolean(key))
            elif key in ['color', 'flash_color']:
                setattr(Firefly, key, config.get(key))
            elif key in ['min_interval', 'max_interval',
                         'min_flash', 'max_flash']:
                setattr(Firefly, key, config.getint(key))
            else:
                setattr(Firefly, key, config.getfloat(key))

    @staticmethod
    def clamp_interval(cycles: int) -> int:
        return max(Firefly.min_interval, min(cycles, Firefly.max_interval))

    def separation(self, flies):
        steering = pg.Vector2()
        for fly in flies:
            dist = self.position.distance_to(fly.position)
            if dist < self.crowding:
                steering -= fly.position - self.position
        steering = self.clamp_force(steering)
        return steering

    def alignment(self, flies):
        steering = pg.Vector2()
        for fly in flies:
            steering += fly.velocity
        steering /= len(flies)
        steering -= self.velocity
        steering = self.clamp_force(steering)
        return steering / 8

    def cohesion(self, flies):
        steering = pg.Vector2()
        for fly in flies:
            steering += fly.position
        steering /= len(flies)
        steering -= self.position
        steering = self.clamp_force(steering)
        return steering / 100

    def synchronize(self, flies):
        steering = 0
        for fly in flies:
            steering += fly.is_flashing
            steering /= float(len(flies))
            return steering

    def update(self, dt, flies):
        steering = pg.Vector2()

        if not self.can_wrap:
            steering += self.avoid_edge()

        neighbors = self.get_neighbors(flies)
        if neighbors:

            separation = self.separation(neighbors)
            alignment = self.alignment(neighbors)
            cohesion = self.cohesion(neighbors)
            sync = self.synchronize(neighbors)

            # DEBUG
            # separation *= 0
            # alignment *= 0
            # cohesion *= 0

            steering += separation + alignment + cohesion

            if not self.is_flashing:
                cycle_diff = int(abs(self.flash_cycle - self.flash_interval)
                                 * sync)
                if self.flash_cycle < self.flash_interval / 2:
                    self.flash_interval = self.clamp_interval(self.flash_interval + cycle_diff)
                    self.flash_cycle += cycle_diff
                    # self.flash_cycle = self.clamp_interval(self.flash_cycle - randint(0, cycle_diff))
                else:
                    self.flash_interval = self.clamp_interval(self.flash_interval - cycle_diff)
                    # self.flash_cycle = self.clamp_interval(self.flash_cycle + randint(0, cycle_diff))

            if self.flash_interval < self.flash_length * 2:
                self.flash_interval *= 2

        if self.flash_cycle > self.flash_interval:
            if self.flash_cycle < self.flash_interval + self.flash_length:
                self.is_flashing = True
            else:
                self.flash_cycle -= self.flash_interval
                self.is_flashing = False

        self.flash_cycle += 1

        super().update(dt, steering, self.is_flashing)

    def get_neighbors(self, flies):
        neighbors = []
        for fly in flies:
            if fly != self:
                dist = self.position.distance_to(fly.position)
                if dist < self.perception:
                    neighbors.append(fly)
        return neighbors

import pygame as pg
from random import uniform
from vehicle import Vehicle


class Firefly(Vehicle):

    # CONFIG
    debug = False
    min_speed = .01
    max_speed = .2
    max_force = 1
    max_turn = 5
    perception = 60
    crowding = 15
    can_wrap = False
    edge_distance_pct = 5
    ###############

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
                         Firefly.max_force, Firefly.can_wrap)

        self.rect = self.image.get_rect(center=self.position)

        self.debug = Firefly.debug

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

    def update(self, dt, flies):
        steering = pg.Vector2()

        if not self.can_wrap:
            steering += self.avoid_edge()

        neighbors = self.get_neighbors(flies)
        if neighbors:

            separation = self.separation(neighbors)
            alignment = self.alignment(neighbors)
            cohesion = self.cohesion(neighbors)

            # DEBUG
            # separation *= 0
            # alignment *= 0
            # cohesion *= 0

            steering += separation + alignment + cohesion

        # steering = self.clamp_force(steering)

        super().update(dt, steering)

    def get_neighbors(self, flies):
        neighbors = []
        for fly in flies:
            if fly != self:
                dist = self.position.distance_to(fly.position)
                if dist < self.perception:
                    neighbors.append(fly)
        return neighbors

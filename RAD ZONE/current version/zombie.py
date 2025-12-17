import pygame

class Zombie:
    def __init__(self, x, y):
        self._pos = pygame.Vector2(x, y)
        self._speed = 80
        self._radius = 20
        self._alive = True

    def update(self, dt, player_world_pos):
        if not self._alive:
            return

        direction = player_world_pos - self._pos
        if direction.length() > 0:
            direction = direction.normalize()
            self._pos += direction * self._speed * dt

    def draw(self, screen, camera_pos):
        screen_pos = self._pos - camera_pos
        pygame.draw.circle(screen, (0, 180, 0), screen_pos, self._radius)

    def take_damage(self, dmg):
        self._alive = False

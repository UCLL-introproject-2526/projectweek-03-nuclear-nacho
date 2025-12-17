import pygame

class Camera:
    def __init__(self, x, y):
        self._pos = pygame.Vector2(x, y)

    # -------- GETTER --------
    def get_position(self):
        return self._pos

    # -------- LOGIC --------
    def update(self, keys, speed, dt):
        if keys[pygame.K_z]:
            self._pos.y -= speed * dt
        if keys[pygame.K_s]:
            self._pos.y += speed * dt
        if keys[pygame.K_q]:
            self._pos.x -= speed * dt
        if keys[pygame.K_d]:
            self._pos.x += speed * dt

import pygame

class Player:
    def __init__(self, surf, rect):
        self._surf = surf
        self._rect = rect

        self._max_stamina = 100
        self._stamina = self._max_stamina

        self._drain = 40
        self._regen = 15

        self._exhaust_at = 0
        self._recover_at = 20
        self._exhausted = False

        self._base_speed = 200
        self._sprint_speed = 300
        self._speed = self._base_speed

    # -------- GETTERS --------
    def get_rect(self):
        return self._rect

    def get_surface(self):
        return self._surf

    def get_speed(self):
        return self._speed

    def get_stamina(self):
        return self._stamina

    def is_exhausted(self):
        return self._exhausted

    # -------- LOGIC --------
    def update(self, keys, dt):
        moving = keys[pygame.K_z] or keys[pygame.K_q] or keys[pygame.K_s] or keys[pygame.K_d]
        sprinting = keys[pygame.K_LSHIFT] and moving

        if self._stamina <= self._exhaust_at:
            self._exhausted = True
        elif self._stamina >= self._recover_at:
            self._exhausted = False

        if sprinting and not self._exhausted:
            self._stamina -= self._drain * dt
            self._speed = self._sprint_speed
        else:
            self._stamina += self._regen * dt
            self._speed = self._base_speed

        self._stamina = max(0, min(self._stamina, self._max_stamina))

    def draw(self, screen):
        screen.blit(self._surf, self._rect)

import pygame

class UI:
    def __init__(self, health, stamina, outline):
        self._health_surf, self._health_rect = health
        self._stamina_surf, self._stamina_rect = stamina
        self._outline_surf = outline[0]

    def draw(self, screen, health, max_health, stamina, max_stamina):
        # ---------- HEALTH (SHRINKS) ----------
        health_ratio = 0 if max_health <= 0 else max(0, min(health / max_health, 1))
        health_pos = self._health_rect.topleft

        if health_ratio > 0:
            width = int(self._health_surf.get_width() * health_ratio)
            health_part = self._health_surf.subsurface(
                (0, 0, width, self._health_surf.get_height())
            )
            screen.blit(health_part, health_pos)

        # Health outline on top
        screen.blit(self._outline_surf, health_pos)

        # ---------- STAMINA (SHRINKS) ----------
        stamina_ratio = 0 if max_stamina <= 0 else max(0, min(stamina / max_stamina, 1))
        stamina_pos = self._stamina_rect.topleft

        if stamina_ratio > 0:
            width = int(self._stamina_surf.get_width() * stamina_ratio)
            stamina_part = self._stamina_surf.subsurface(
                (0, 0, width, self._stamina_surf.get_height())
            )
            screen.blit(stamina_part, stamina_pos)

        screen.blit(self._outline_surf, stamina_pos)

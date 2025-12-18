class UI:
    def __init__(self, health, stamina, outline):
        self._health_surf, self._health_rect = health
        self._stamina_surf, self._stamina_rect = stamina
        self._outline_surf = outline[0]

    def draw(self, screen, health, max_health, stamina, max_stamina):
        # ---------- HEALTH (STATIC) ----------
        health_pos = self._health_rect.topleft

        # Draw full health bar
        screen.blit(self._health_surf, health_pos)

        # Draw health outline
        screen.blit(self._outline_surf, health_pos)

        # ---------- STAMINA (SHRINKS) ----------
        stamina_ratio = max(0, min(stamina / max_stamina, 1))
        stamina_pos = self._stamina_rect.topleft

        # Draw filled stamina only
        if stamina_ratio > 0:
            width = int(self._stamina_surf.get_width() * stamina_ratio)
            stamina_part = self._stamina_surf.subsurface(
                (0, 0, width, self._stamina_surf.get_height())
            )
            screen.blit(stamina_part, stamina_pos)

        # Draw stamina outline last
        screen.blit(self._outline_surf, stamina_pos)


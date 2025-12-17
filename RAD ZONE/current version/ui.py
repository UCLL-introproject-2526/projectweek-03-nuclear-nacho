class UI:
    def __init__(self, health, stamina, outline):
        self._health = health
        self._stamina = stamina
        self._outline = outline

    def draw(self, screen, stamina_value):
        ratio = stamina_value / 100
        ratio = max(0, min(ratio, 1))

        if ratio > 0:
            width = int(self._stamina[0].get_width() * ratio)
            part = self._stamina[0].subsurface(
                (0, 0, width, self._stamina[0].get_height())
            )
            screen.blit(part, self._stamina[1].topleft)

        screen.blit(self._health[0], self._health[1])
        screen.blit(self._outline[0], self._health[1])
        screen.blit(self._outline[0], self._stamina[1])

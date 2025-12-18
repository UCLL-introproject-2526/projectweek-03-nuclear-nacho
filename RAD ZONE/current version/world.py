class World:
    def __init__(self, map_surf, buildings):
        self._map = map_surf
        self._buildings = buildings

    def draw(self, screen, camera):
        screen.blit(self._map, -camera.get_position())

        for surf, pos in self._buildings:
            rect = surf.get_rect(topleft=pos)
            screen.blit(surf, camera.apply(rect))


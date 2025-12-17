class World:
    def __init__(self, map_surf, buildings):
        self._map = map_surf
        self._buildings = buildings

    def draw(self, screen, camera):
        cam = camera.get_position()
        screen.blit(self._map, (-cam.x, -cam.y))

        for surf, pos in self._buildings:
            screen.blit(surf, pos - cam)

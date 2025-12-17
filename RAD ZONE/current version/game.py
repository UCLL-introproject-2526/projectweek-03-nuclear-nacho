import pygame
from sys import exit

from player import Player
from camera import Camera
from world import World
from ui import UI
from minimap import Minimap
from assets import ImageLoader
from sound_manager import SoundManager




def load_building(path, size, x, y):
    surf = ImageLoader.load(path, size=size)[0]
    return surf, pygame.Vector2(x, y)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.sound = SoundManager()

        self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        w, h = self._screen.get_size()

        # Load assets
        map_surf, _ = ImageLoader.load("RAD ZONE/current version/Graphics/Game_building_test.png", size=(7680, 6400))
        char_surf, char_rect = ImageLoader.load(
            "RAD ZONE/current version/Graphics/AChar.png", size=(150, 150), center=(w // 2, h // 2)
        )

        health = ImageLoader.load("RAD ZONE/current version/Graphics/Health-bar.png", size=(512, 35), center=(260, 30))
        stamina = ImageLoader.load("RAD ZONE/current version/Graphics/Stamina-bar.png", size=(512, 35), center=(260, 70))
        outline = ImageLoader.load("RAD ZONE/current version/Graphics/Border-bar.png", size=(512, 35))

        buildings = [
            load_building("RAD ZONE/current version/Graphics/Building7.png", (400, 768), 1722, 1068),
        ]

            # load_building("RAD ZONE/current version/Graphics/Building2.png", (350, 350), 1950, 800),
            # load_building("RAD ZONE/current version/Graphics/Building3.png", (350, 350), 1250, 800),
            # load_building("RAD ZONE/current version/Graphics/Building4.png", (350, 350), 900, 800),
            # load_building("RAD ZONE/current version/Graphics/Building5.png", (350, 350), 550, 800),

        # buildings = [
        #     (ImageLoader.load(f"RAD ZONE/current version/Graphics/Building{i}.png", size=(350, 350))[0],
        #      pygame.Vector2(1600 - (i - 1) * 350, 800))
        #     for i in range(1, 6)
        # ]

            # (load_image("Graphics/Building2.png", size=(700, 700))[0], pygame.Vector2(1950, 800)),
            # (load_image("Graphics/Building3.png", size=(700, 700))[0], pygame.Vector2(1250, 800)),
            # (load_image("Graphics/Building4.png", size=(700, 700))[0], pygame.Vector2(900, 800)),
            # (load_image("Graphics/Building5.png", size=(700, 700))[0], pygame.Vector2(550, 800)),
            
        # Create objects
        self._player = Player(char_surf, char_rect, self.sound)
        self._camera = Camera(
            map_surf.get_width() // 2 - char_rect.centerx,
            map_surf.get_height() // 2 - char_rect.centery
        )
        self._world = World(map_surf, buildings)
        self._ui = UI(health, stamina, outline)
        self._minimap = Minimap(map_surf, buildings, (w, h))

    def run(self):
        while True:
            dt = self._clock.tick(60) / 1000  # Delta time in seconds
            current_time = pygame.time.get_ticks() / 1000  # Current time in seconds

            # ---- EVENT HANDLING ----
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                # Weapon cycling with mouse wheel
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self._player.next_weapon()
                    else:
                        self._player.previous_weapon()

            # ---- INPUT STATES ----
            keys = pygame.key.get_pressed()

            # ---- UPDATE GAME OBJECTS ----
            self._player.update(keys, dt, current_time)
            self._camera.update(keys, self._player.get_speed(), dt)

            # ---- DRAW ----
            self._screen.fill((0, 0, 0))
            self._world.draw(self._screen, self._camera)
            self._player.draw(self._screen)
            self._ui.draw(self._screen, self._player.get_stamina())

            player_world_pos = self._camera.get_position() + self._player.get_rect().center
            self._minimap.draw(self._screen, player_world_pos)

            # ---- REFRESH DISPLAY ----
            pygame.display.flip()

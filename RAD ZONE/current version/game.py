import pygame
from sys import exit

from player import Player
from camera import Camera
from world import World
from ui import UI
from minimap import Minimap
from assets import ImageLoader
from inventory import Inventory
from hoofdscherm import Menu


def load_building(path, size, x, y):
    surf = ImageLoader.load(path, size=size)[0]
    return surf, pygame.Vector2(x, y)


class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(0)
        self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        w, h = self._screen.get_size()

        # Load assets
        map_surf, _ = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Game_building_test.png",
            size=(7680, 6400)
        )
        char_surf, char_rect = ImageLoader.load(
            "RAD ZONE/current version/Graphics/AChar.png",
            size=(150, 150),
            center=(w // 2, h // 2)
        )

        health = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Health-bar.png",
            size=(512, 35),
            center=(260, 30)
        )
        stamina = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Stamina-bar.png",
            size=(512, 35),
            center=(260, 70)
        )
        outline = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Border-bar.png",
            size=(512, 35)
        )

        buildings = [
            load_building(
                "RAD ZONE/current version/Graphics/Building7.png",
                (400, 768),
                1722,
                1068
            ),
        ]

        # Create objects
        self._player = Player(char_surf, char_rect)
        self._camera = Camera(
            map_surf.get_width() // 2 - char_rect.centerx,
            map_surf.get_height() // 2 - char_rect.centery
        )
        self._world = World(map_surf, buildings)
        self._ui = UI(health, stamina, outline)
        self._minimap = Minimap(map_surf, buildings, (w, h))

        def load_icon(path):
            return ImageLoader.load(path, size=(48, 48))[0]

        def load_weapon(path):
            return ImageLoader.load(path, size=(96, 96))[0]

        item_data = {
            "pistol": {
                "icon": load_icon("RAD ZONE/current version/Graphics/pistool.png"),
                "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/pistool.png")
            },
            "shotgun": {
                "icon": load_icon("RAD ZONE/current version/Graphics/shotgun.png"),
                "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/shotgun.png")
            },
            "machine_gun": {
                "icon": load_icon("RAD ZONE/current version/Graphics/machine_gun.png"),
                "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/machine_gun.png")
            },
            "revolver": {
                "icon": load_icon("RAD ZONE/current version/Graphics/revolver.png"),
                "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/revolver.png")
            },
            "crossbow": {
                "icon": load_icon("RAD ZONE/current version/Graphics/crossbow.png"),
                "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/crossbow.png")
            },
            "knife": {
                "icon": load_icon("RAD ZONE/current version/Graphics/knife.png"),
                "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/knife.png")
            }
        }

        iodine_icon = load_icon("RAD ZONE/current version/Graphics/Iodine pills.png")
        iodine_icon = pygame.transform.scale(
            iodine_icon,
            (
                int(iodine_icon.get_width() * 2),
                int(iodine_icon.get_height() * 2)
            )
        )

        item_data["iodine"] = {
            "icon": iodine_icon,
            "weapon_surf": None,
            "stackable": True,
            "amount": 5,
            "max_stack": 20
        }

        item_data.update({
            "bandage": {
                "icon": load_icon("RAD ZONE/current version/Graphics/bandage.png"),
                "weapon_surf": None,
                "stackable": True,
                "amount": 3,
                "max_stack": 10
            },
            "energy_drink": {
                "icon": load_icon("RAD ZONE/current version/Graphics/Energy drink.png"),
                "weapon_surf": None,
                "stackable": True,
                "amount": 2,
                "max_stack": 5
            }
        })

        socket_surf = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Inventory_box.png",
            size=(64, 64)
        )[0]

        self._inventory_key_down = False
        self._inventory = Inventory(socket_surf, item_data, (w, h))

        # --------- HOOFDMENU OBJECT ----------
        self._menu = Menu(
            self._screen,
            ["Start Game", "Scoreboard", "Settings", "Credits", "Exit Game"]
        )

    def run(self):
        # ---------- EERST HOOFDMENU ----------
        choice = self._menu.run()

        if choice == "Exit Game":
            pygame.quit()
            exit()

        # Later kan je hier scoreboard / settings / credits afhandelen
        # Voor nu: bij "Start Game" of iets anders → game starten

        # ---------- GAME LOOP ----------
        while True:
            dt = self._clock.tick(60) / 1000

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            mouse_down = mouse_pressed[0]
            mouse_up = not mouse_pressed[0]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e and not self._inventory_key_down:
                        self._inventory.toggle()
                        self._inventory_key_down = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_e:
                        self._inventory_key_down = False

            keys = pygame.key.get_pressed()

            self._player.update(keys, dt)
            self._camera.update(keys, self._player.get_speed(), dt)

            self._screen.fill((0, 0, 0))

            self._world.draw(self._screen, self._camera)
            self._player.draw(self._screen)

            self._ui.draw(self._screen, self._player.get_stamina())

            player_world_pos = (
                self._camera.get_position() +
                self._player.get_rect().center
            )
            self._minimap.draw(self._screen, player_world_pos)

            self._inventory.draw(self._screen)
            self._inventory.handle_hotbar_keys(keys)
            self._inventory.update(mouse_pos, mouse_down, mouse_up)

            pygame.display.flip()

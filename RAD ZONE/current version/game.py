import pygame
from sys import exit

from player import Player
from camera import Camera
from world import World
from ui import UI
from minimap import Minimap
from assets import ImageLoader
from sound_manager import SoundManager
from inventory import Inventory
from hoofdscherm import Menu
from Zombie import ZombieSpawner
from scoreboard import Scoreboard


def load_building(path, size, x, y):
    surf = ImageLoader.load(path, size=size)[0]
    return surf, pygame.Vector2(x, y)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()
        pygame.key.set_repeat(0)

        w, h = self._screen.get_size()

        # Sound manager
        self.sound = SoundManager()

        # HOOFDMENU
        self._menu = Menu(self._screen, ["Play", "Scoreboard", "Settings", "Credits", "Quit"])

        # LOAD ASSETS
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
            load_building("RAD ZONE/current version/Graphics/Building7.png", (400, 768), 1722, 1068)
        ]

        # OBJECTEN
        self._player = Player(char_surf, char_rect, self.sound)
        self._camera = Camera(w, h)
        self._world = World(map_surf, buildings)
        self._ui = UI(health, stamina, outline)
        self._minimap = Minimap(map_surf, buildings, (w, h))
        self._zombie_spawner = ZombieSpawner()

        # INVENTORY
        self._inventory_key_down = False
        self._inventory = self._create_inventory((w, h))

        # KNIFE LOGIC
        self._last_f_press_time = -1
        self._last_stabbed_zombies = set()
        self._f_key_was_pressed = False

    # ---------------- HELPERS ----------------
    def _create_inventory(self, screen_size):
        def load_icon(path): return ImageLoader.load(path, size=(48, 48))[0]
        def load_weapon(path): return ImageLoader.load(path, size=(96, 96))[0]

        item_data = {
            "pistol": {"icon": load_icon("RAD ZONE/current version/Graphics/pistool.png"),
                       "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/pistool.png")},
            "shotgun": {"icon": load_icon("RAD ZONE/current version/Graphics/shotgun.png"),
                        "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/shotgun.png")},
            "rifle": {"icon": load_icon("RAD ZONE/current version/Graphics/machine_gun.png"),
                      "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/machine_gun.png")},
            "revolver": {"icon": load_icon("RAD ZONE/current version/Graphics/revolver.png"),
                         "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/revolver.png")},
            "crossbow": {"icon": load_icon("RAD ZONE/current version/Graphics/crossbow.png"),
                         "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/crossbow.png")},
            "knife": {"icon": load_icon("RAD ZONE/current version/Graphics/knife.png"),
                      "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/knife.png")}
        }

        iodine_icon = load_icon("RAD ZONE/current version/Graphics/Iodine pills.png")
        iodine_icon = pygame.transform.scale(iodine_icon, (iodine_icon.get_width() * 2, iodine_icon.get_height() * 2))
        item_data.update({
            "iodine": {"icon": iodine_icon, "weapon_surf": None, "stackable": True, "amount": 5, "max_stack": 20},
            "bandage": {"icon": load_icon("RAD ZONE/current version/Graphics/bandage.png"),
                        "weapon_surf": None, "stackable": True, "amount": 3, "max_stack": 10},
            "energy_drink": {"icon": load_icon("RAD ZONE/current version/Graphics/Energy drink.png"),
                             "weapon_surf": None, "stackable": True, "amount": 2, "max_stack": 5}
        })

        socket_surf = ImageLoader.load("RAD ZONE/current version/Graphics/Inventory_box.png", size=(64, 64))[0]
        inventory_bg = ImageLoader.load("RAD ZONE/current version/Graphics/Inventory_background.png")[0]
        hotbar_bg = ImageLoader.load("RAD ZONE/current version/Graphics/Hotbar_background.png")[0]

        return Inventory(socket_surf, item_data, screen_size, inventory_bg, hotbar_bg, self._player)

    # ---------------- GAME LOOP ----------------
    def run(self):
        choice = self._menu.run()
        if choice == "Quit":
            pygame.quit()
            exit()
        if choice == "Scoreboard":
            Scoreboard(self._screen).run()
            return self.run()

        while True:
            dt = self._clock.tick(60) / 1000
            current_time = pygame.time.get_ticks() / 1000

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            mouse_down = mouse_pressed[0]
            mouse_up = not mouse_pressed[0]

            keys = pygame.key.get_pressed()
            self._handle_events()

            # UPDATE OBJECTS
            self._player.update(keys, dt, current_time)
            player_pos = pygame.Vector2(self._player.get_rect().center)
            self._camera.update(player_pos)
            self._zombie_spawner.update(player_pos, dt, current_time)

            # Knife logic
            self._handle_knife(keys, current_time, player_pos)

            # Zombie attacks
            self._handle_zombie_attacks(player_pos, dt)

            # DRAW
            self._screen.fill((0, 0, 0))
            self._world.draw(self._screen, self._camera)

            drawables = [("player", self._player, player_pos.y)]
            for zombie in self._zombie_spawner.get_zombies():
                drawables.append(("zombie", zombie, zombie.get_position().y))
            for obj_type, obj, _ in sorted(drawables, key=lambda x: x[2]):
                if obj_type == "player":
                    obj.draw(self._screen)
                else:
                    obj.draw(self._screen, self._camera)

            # ---------- UI ----------
            self._ui.draw(
                self._screen,
                self._player.get_health() / self._player.get_max_health(),  # 0-1
                self._player.get_stamina_display(),  # 0-1
                dt=dt
            )

            self._minimap.draw(self._screen, player_pos)
            self._inventory.draw(self._screen)
            self._inventory.handle_hotbar_keys(keys)
            self._inventory.update(mouse_pos, mouse_down, mouse_up)

            pygame.display.flip()

    # ---------------- EVENT HANDLING ----------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self._player.next_weapon()
                else:
                    self._player.previous_weapon()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e and not self._inventory_key_down:
                self._inventory.toggle()
                self._inventory_key_down = True
            if event.type == pygame.KEYUP and event.key == pygame.K_e:
                self._inventory_key_down = False

    # ---------------- KNIFE LOGIC ----------------
    def _handle_knife(self, keys, current_time, player_pos):
        f_pressed = keys[pygame.K_f]
        if f_pressed and not self._f_key_was_pressed and self._player.weapon.name == "knife":
            self._last_f_press_time = current_time
            self._last_stabbed_zombies = set()
            self._f_key_was_pressed = True
        elif not f_pressed:
            self._f_key_was_pressed = False

        if current_time - self._last_f_press_time < 0.5 and self._player.weapon.name == "knife":
            for zombie in self._zombie_spawner.get_zombies():
                if zombie not in self._last_stabbed_zombies and not zombie.is_dead():
                    if (zombie.get_position() - player_pos).length() < 100:
                        zombie.take_damage(50, zombie.get_position() - player_pos, current_time)
                        self._last_stabbed_zombies.add(zombie)

    # ---------------- ZOMBIE ATTACKS ----------------
    def _handle_zombie_attacks(self, player_pos, dt):
        for zombie in self._zombie_spawner.get_zombies():
            if zombie.is_attacking() and (zombie.get_position() - player_pos).length() < 60:
                self._player.take_damage(zombie._damage_per_second * dt)

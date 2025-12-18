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
from pause_menu import PauseMenu
from death_screen import DeathScreen


def load_building(path, size, x, y):
    surf = ImageLoader.load(path, size=size)[0]
    return surf, pygame.Vector2(x, y)


def load_char_weapon(path):
    return ImageLoader.load(path, size=(96, 96))[0]


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()
        pygame.key.set_repeat(0)

        # GELUID & HOOFDMENU
        self.sound = SoundManager()
        self._menu = Menu(self._screen, ["Play", "Scoreboard", "Settings", "Credits", "Quit"])

        # --------------- GAME STATE ---------------
        self.state = "MENU"

        # OBJECTEN ---------- starten als NONE
        self._player = None
        self._world = None
        self._camera = None
        self._ui = None
        self._inventory = None
        self._zombie_spawner = None
        self._minimap = None

        w, h = self._screen.get_size()

        # LOAD ASSETS
        self.map_surf, _ = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Game_building_test.png",
            size=(7680, 6400)
        )
        self.char_surf, self.char_rect = ImageLoader.load(
            "RAD ZONE/current version/Graphics/AChar.png",
            size=(150, 150),
            center=(w // 2, h // 2)
        )
        self.health = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Health-bar.png",
            size=(512, 35),
            center=(260, 30)
        )
        self.stamina = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Stamina-bar.png",
            size=(512, 35),
            center=(260, 70)
        )
        self.outline = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Border-bar.png",
            size=(512, 35)
        )
        self.buildings = [
            load_building("RAD ZONE/current version/Graphics/Building7.png", (400, 768), 1722, 1068)
        ]

        # INVENTORY
        self._inventory = None
        self._inventory_key_down = False

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
                       "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/pistool.png"),
                       "char_weapon": load_char_weapon("RAD ZONE/current version/Graphics/char_pistool.png")},
            "shotgun": {"icon": load_icon("RAD ZONE/current version/Graphics/shotgun.png"),
                        "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/shotgun.png"),
                        "char_weapon": load_char_weapon("RAD ZONE/current version/Graphics/char_shotgun.png")},
            "rifle": {"icon": load_icon("RAD ZONE/current version/Graphics/machine_gun.png"),
                      "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/machine_gun.png"),
                      "char_weapon": load_char_weapon("RAD ZONE/current version/Graphics/char_machine_gun.png")},
            "revolver": {"icon": load_icon("RAD ZONE/current version/Graphics/revolver.png"),
                         "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/revolver.png"),
                         "char_weapon": load_char_weapon("RAD ZONE/current version/Graphics/char_revolver.png")},
            "crossbow": {"icon": load_icon("RAD ZONE/current version/Graphics/crossbow.png"),
                         "weapon_surf": load_weapon("RAD ZONE/current version/Graphics/crossbow.png"),
                         "char_weapon": load_char_weapon("RAD ZONE/current version/Graphics/char_crossbow.png")},
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

    # ---------------- START GAME ----------------
    def start_game(self):
        w, h = self._screen.get_size()
        self._player = Player(self.char_surf, self.char_rect, self.sound)
        self._camera = Camera(w, h)
        self._world = World(self.map_surf, self.buildings)
        self._ui = UI(self.health, self.stamina, self.outline)
        self._minimap = Minimap(self.map_surf, self.buildings, (w, h))
        self._zombie_spawner = ZombieSpawner()
        self._inventory = self._create_inventory((w, h))
        self._inventory_key_down = False

    # ---------------- GAME LOOP ----------------
    def run(self):
        while True:
            if self.state == "MENU":
                choice = self._menu.run()
                if choice == "Quit":
                    pygame.quit()
                    exit()
                elif choice == "Scoreboard":
                    Scoreboard(self._screen).run()
                    continue
                elif choice == "Play":
                    self.start_game()
                    self.state = "PLAYING"

            elif self.state == "PLAYING":
                self._game_loop()

    # ---------------- GAMEPLAY LOOP ----------------
    def _game_loop(self):
        while self.state == "PLAYING":
            dt = self._clock.tick(60) / 1000
            current_time = pygame.time.get_ticks() / 1000
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            mouse_down = mouse_pressed[0]
            mouse_up = not mouse_pressed[0]

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if self._inventory and event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self._inventory.select_next()
                    else:
                        self._inventory.select_previous()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e and self._inventory and not self._inventory_key_down:
                        self._inventory.toggle()
                        self._inventory_key_down = True
                    if event.key == pygame.K_ESCAPE:
                        action = PauseMenu(self._screen).run(self._screen.copy())
                        if action == "Resume":
                            pass
                        elif action == "Quit":
                            self.state = "MENU"
                            return  # stop gameplay loop veilig
                        elif action == "Settings":
                            print("Open Settings menu")
                        elif action == "CommitScore":
                            print("Open Commit Score menu")
                if event.type == pygame.KEYUP and event.key == pygame.K_e:
                    self._inventory_key_down = False

            keys = pygame.key.get_pressed()

            # ---------------- GAMEPLAY ----------------
            if self._player:
                self._player.update(keys, dt, current_time)
                player_pos = pygame.Vector2(self._player.get_rect().center)
            if self._camera and self._player:
                self._camera.update(player_pos)
            if self._zombie_spawner and self._player:
                self._zombie_spawner.update(player_pos, dt, current_time)

            self._handle_knife(keys, current_time, player_pos)
            self._handle_zombie_attacks(player_pos, dt)

            # Drawing
            self._screen.fill((0, 0, 0))
            if self._world:
                self._world.draw(self._screen, self._camera)
            self._player.set_equipped_item(self._inventory.get_equipped_item())

            drawables = [("player", self._player, player_pos.y)]
            if self._zombie_spawner:
                for zombie in self._zombie_spawner.get_zombies():
                    drawables.append(("zombie", zombie, zombie.get_position().y))
            for obj_type, obj, _ in sorted(drawables, key=lambda x: x[2]):
                if obj_type == "player":
                    obj.draw(self._screen)
                else:
                    obj.draw(self._screen, self._camera)

            if self._ui:
                self._ui.draw(self._screen,
                              self._player.get_health(),
                              self._player.get_max_health(),
                              self._player.get_stamina(),
                              100)
            if self._minimap:
                self._minimap.draw(self._screen, player_pos)
            if self._inventory:
                self._inventory.draw(self._screen)
                self._inventory.update(mouse_pos, mouse_down, mouse_up)

            pygame.display.flip()

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

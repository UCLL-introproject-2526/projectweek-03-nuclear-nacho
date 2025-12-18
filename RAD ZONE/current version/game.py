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


def load_building(path, size, x, y):
    surf = ImageLoader.load(path, size=size)[0]
    return surf, pygame.Vector2(x, y)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.sound = SoundManager()

        pygame.key.set_repeat(0)
        self._screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        w, h = self._screen.get_size()

        # --------- HOOFDMENU OBJECT ----------
        self._menu = Menu(
            self._screen,
            ["Start Game", "Scoreboard", "Settings", "Credits", "Exit Game"]
        )

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
        self._player = Player(char_surf, char_rect, self.sound)
        self._camera = Camera(w, h)

        self._world = World(map_surf, buildings)
        self._ui = UI(health, stamina, outline)
        self._minimap = Minimap(map_surf, buildings, (w, h))
        self._zombie_spawner = ZombieSpawner()

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
            "rifle": {
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

        inventory_bg = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Inventory_background.png"
        )[0]

        hotbar_bg = ImageLoader.load(
            "RAD ZONE/current version/Graphics/Hotbar_background.png"
        )[0]

        
        self._inventory_key_down = False
        self._inventory = Inventory(
            socket_surf,
            item_data,
            (w, h),
            inventory_bg,
            hotbar_bg
        )
        
        # Stab tracking for damage
        self._last_stab_time = -1
        self._stab_damage_cooldown = 0.1  # Prevent multiple hits per stab
        self._last_stabbed_zombies = set()  # Track which zombies we've hit this stab
        self._last_f_press_time = -1  # Track when F was last pressed for damage

        # --------- HOOFDMENU OBJECT ----------
        self._menu = Menu(
            self._screen,
            ["Start Game", "Scoreboard", "Settings", "Credits", "Exit Game"]
        )

            # ---- EVENT HANDLING ----

        # ---------- EERST HOOFDMENU ----------
    def run(self):
        # ---------- HOOFDMENU ----------
        choice = self._menu.run()

        if choice == "Exit Game":
            pygame.quit()
            exit()

        # ---------- GAME LOOP ----------
        while True:
            dt = self._clock.tick(60) / 1000 # Delta time in seconds
            current_time = pygame.time.get_ticks() / 1000 # Current time in seconds

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()
            mouse_down = mouse_pressed[0]
            mouse_up = not mouse_pressed[0]

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
            # if event.type == pygame.KEYDOWN:
            #         if event.key == pygame.K_e:
            #             self._inventory.toggle()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e and not self._inventory_key_down:
                        self._inventory.toggle()
                        self._inventory_key_down = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_e:
                        self._inventory_key_down = False

            keys = pygame.key.get_pressed()

            self._player.update(keys, dt, current_time)
            self._camera.update(pygame.Vector2(self._player.get_rect().center))
            
            # Update zombies
            player_pos = pygame.Vector2(self._player.get_rect().center)
            self._zombie_spawner.update(player_pos, dt, current_time)
            
            # Check if knife (stab) is being used to damage zombies
            # Detect when F is pressed (going from not pressed to pressed)
            f_pressed = keys[pygame.K_f]
            if f_pressed and not hasattr(self, '_f_key_was_pressed'):
                self._f_key_was_pressed = False
            
            if f_pressed and not self._f_key_was_pressed and self._player.weapon.name == "knife":
                # F just pressed and we have knife
                self._last_f_press_time = current_time
                self._last_stabbed_zombies = set()  # Reset hit zombies
                self._f_key_was_pressed = True
                print(f"[STAB] F pressed! Weapon: {self._player.weapon.name}")
            elif not f_pressed:
                self._f_key_was_pressed = False
            
            # Apply damage if F was recently pressed (within 0.5 seconds for animation duration)
            if current_time - self._last_f_press_time < 0.5 and self._player.weapon.name == "knife":
                damage_count = 0
                for zombie in self._zombie_spawner.get_zombies():
                    if zombie not in self._last_stabbed_zombies and not zombie.is_dead():
                        zombie_pos = zombie.get_position()
                        distance = (zombie_pos - player_pos).length()
                        
                        if distance < 100:
                            knockback_dir = (zombie_pos - player_pos)
                            zombie.take_damage(50, knockback_dir, current_time)
                            self._last_stabbed_zombies.add(zombie)
                            damage_count += 1
                            print(f"[HIT] Zombie damaged! Health: {zombie.get_health()}")
                
                if damage_count > 0:
                    print(f"[DAMAGE] Hit {damage_count} zombies")
            
            # Check zombie attacks on player and apply damage
            for zombie in self._zombie_spawner.get_zombies():
                if zombie.is_attacking():
                    distance = (zombie.get_position() - player_pos).length()
                    if distance < 60:
                        self._player.take_damage(zombie._damage_per_second * dt)

            # ---- DRAW ----

            self._screen.fill((0, 0, 0))
            self._world.draw(self._screen, self._camera)
            
            # Draw player and zombies with proper z-ordering (by y position)
            # Collect all drawable objects
            drawables = []
            drawables.append(("player", self._player, player_pos.y))
            for zombie in self._zombie_spawner.get_zombies():
                drawables.append(("zombie", zombie, zombie.get_position().y))
            
            # Sort by y position (lower on screen = drawn last = on top)
            drawables.sort(key=lambda x: x[2])
            
            # Draw all objects
            for obj_type, obj, _ in drawables:
                if obj_type == "player":
                    self._player.draw(self._screen)
                else:
                    obj.draw(self._screen, self._camera)
            
            self._ui.draw(self._screen, self._player.get_health(), self._player.get_max_health())

            player_world_pos = pygame.Vector2(self._player.get_rect().center)
            self._minimap.draw(self._screen, player_world_pos)


            self._inventory.draw(self._screen)
            self._inventory.handle_hotbar_keys(keys)
            self._inventory.update(mouse_pos, mouse_down, mouse_up)

            pygame.display.flip()

    # def load_icon(path):
    #     return ImageLoader.load(path, size=(48, 48))[0]

    # def load_weapon(path):
    #     return ImageLoader.load(path, size=(96, 96))[0]

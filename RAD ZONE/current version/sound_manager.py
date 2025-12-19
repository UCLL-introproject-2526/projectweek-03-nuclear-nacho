import pygame
import random

import pygame
import random

class SoundManager:
    def __init__(self):
        # Ensure mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Weapon sounds
        self.weapon = {
            "pistol": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/shoot_pistol.mp3"),
                "reload": pygame.mixer.Sound("RAD ZONE/current version/MP3/reload_pistol.mp3"),
                "equip": pygame.mixer.Sound("RAD ZONE/current version/MP3/equip_pistol.mp3"),
            },
            "rifle": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/shoot_rifle_single_shot.mp3"),
                "reload": pygame.mixer.Sound("RAD ZONE/current version/MP3/reload_rifle.mp3"),
                "equip": pygame.mixer.Sound("RAD ZONE/current version/MP3/equip_rifle.mp3"),
            },
            "revolver": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/shoot_revolver.mp3"),
                "reload": pygame.mixer.Sound("RAD ZONE/current version/MP3/revolver_reload.mp3"),
                "equip": pygame.mixer.Sound("RAD ZONE/current version/MP3/revolver_reload.mp3"),
            },
            "shotgun": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/shoot_shotgun.mp3"),
                "reload": pygame.mixer.Sound("RAD ZONE/current version/MP3/shotgun_reload.mp3"),
                "equip": pygame.mixer.Sound("RAD ZONE/current version/MP3/equip_shotgun.mp3"),
            },
            "knife": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/knife_slash.mp3"),
                "equip": pygame.mixer.Sound("RAD ZONE/current version/MP3/knife_slash.mp3"),
                "reload": None
            },
            "crossbow": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/shoot_crossbow.mp3"),
                "equip": None,
                "reload": None,
            }
        }

        # Item sounds
        self.items = {
            "pickup_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_bandages.mp3"),
            "pickup_iodine_pills": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_iodine_pills.mp3"),
            "use_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_bandages.mp3"),
            "use_iodine": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_iodine_pills.mp3"),
        }

        # Zombie death sounds
        self.zombie_death = [
            pygame.mixer.Sound(f"RAD ZONE/current version/MP3/zomdie_die_{i}.mp3")
            for i in range(1, 17)
        ]

        # Player hurt sounds
        self.player_hurt = [
            pygame.mixer.Sound(f"RAD ZONE/current version/MP3/player_take_damage_{i}.mp3")
            for i in range(1, 6)
        ]

        # Current equip sound tracking
        self._current_equip_sound = None

    # ---------------------- PLAYER HURT ----------------------
    def play_player_hurt(self):
        random.choice(self.player_hurt).play()

    # ---------------------- WEAPON ----------------------
    def play_weapon(self, weapon, action):
        sound = self.weapon[weapon].get(action)
        if not sound:
            return
        if action == "equip":
            if self._current_equip_sound:
                self._current_equip_sound.stop()
            self._current_equip_sound = sound
        sound.play()

    # ---------------------- ITEM ----------------------
    def play_item(self, name):
        self.items[name].play()

    # ---------------------- ZOMBIE ----------------------
    def play_zombie_death(self):
        random.choice(self.zombie_death).play()

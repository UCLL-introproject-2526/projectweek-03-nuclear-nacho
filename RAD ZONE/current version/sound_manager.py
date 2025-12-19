import pygame
import random

class SoundManager:
    def __init__(self):
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
                "equip": None,
            },
            "shotgun": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/shoot_shotgun.mp3"),
                "reload": pygame.mixer.Sound("RAD ZONE/current version/MP3/shotgun_reload_open.mp3"),
                "equip": None,
            },
            "knife": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/knife_slash.mp3"),
                "equip": pygame.mixer.Sound("RAD ZONE/current version/MP3/knife_slash.mp3"),  # can be same as shoot
                "reload": None  # optional, just to match the interface
            },
            "crossbow": {
                "shoot": pygame.mixer.Sound("RAD ZONE/current version/MP3/shoot_crossbow.mp3"),
                "equip": None,
                "reload": None,
            }


        }


        self.items = {
            "pickup_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_bandages.mp3"),
            "pickup_iodine_pills": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_iodine_pills.mp3"),
            "use_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_bandages.mp3"),
            "use_iodine": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_iodine_pills.mp3"),
        }

# TERUG IN COMMENTEN WANNEER AUDIOFILES VAN ZOMBIES_DEATH BESCHIKBAAR ZIJN.
        self.zombie_death = [
        pygame.mixer.Sound("RAD ZONE/current version/MP3/scream_wilhelm.mp3")
        for i in range(1, 17)
        ]

        self._current_equip_sound = None

    def play_weapon(self, weapon, action):
        sound = self.weapon[weapon].get(action)
        if not sound:
            return

        # Stop previous equip sound if this is an equip action
        if action == "equip":
            if self._current_equip_sound:
                self._current_equip_sound.stop()
            self._current_equip_sound = sound

        sound.play()

    def play_item(self, name):
        self.items[name].play()

    def play_zombie_death(self):
        random.choice(self.zombie_death).play()
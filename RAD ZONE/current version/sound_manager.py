import pygame
import random

class SoundManager:
    def __init__(self):
        # Ensure mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # ---------------------- WEAPON SOUNDS ----------------------
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

        WEAPON_VOLUME = 0.25   # 👈 adjust to taste (0.0 – 1.0)

        for weapon_actions in self.weapon.values():
            for sound in weapon_actions.values():
                if sound:  # IMPORTANT: skip None values
                    sound.set_volume(WEAPON_VOLUME)



        # ---------------------- ITEM SOUNDS ----------------------
        self.items = {
            "pickup_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_bandages.mp3"),
            "pickup_iodine_pills": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_iodine_pills.mp3"),
            "use_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_bandages.mp3"),
            "use_iodine": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_iodine_pills.mp3"),
        }

        # ---------------------- ZOMBIE DEATH SOUNDS ----------------------
        self.zombie_death = [
            pygame.mixer.Sound(f"RAD ZONE/current version/MP3/zomdie_die_{i}.mp3")
            for i in range(1, 17)
        ]
        for sound in self.zombie_death:
            sound.set_volume(0.5)

        # for sound in self.weapon:
        #     sound.set_volume(0.3)

        # ---------------------- PLAYER HURT SOUNDS ----------------------
        self.player_hurt = [
            pygame.mixer.Sound(f"RAD ZONE/current version/MP3/player_take_damage_{i}.mp3")
            for i in range(1, 6)
        ]
        self._player_hurt_index = 0  # cycle through sounds

        # Create a dedicated channel for player hurt sounds (prevents overlap)
        self._player_hurt_channel = pygame.mixer.Channel(31)

        # Set volume for player hurt sounds
        hurt_volume = 0.5
        for sound in self.player_hurt:
            sound.set_volume(hurt_volume)

        
        # PLAYER DEATH SOUND
        self.player_death = pygame.mixer.Sound("RAD ZONE/current version/MP3/scream_wilhelm.mp3")
        self.player_death.set_volume(0.5)

        # ---------------------- EQUIP SOUND TRACKING ----------------------
        self._current_equip_sound = None

    # ---------------------- PLAYER HURT ----------------------
    def play_player_hurt(self):
        # Only play if the dedicated channel is free
        if not self._player_hurt_channel.get_busy():
            sound = self.player_hurt[self._player_hurt_index]
            self._player_hurt_channel.play(sound)
            self._player_hurt_index = (self._player_hurt_index + 1) % len(self.player_hurt)

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


    # ---------------------- PLAYER DEATH PLAY FUNCTION ----------------------
    def play_player_death(self):
        # Play the death sound on a dedicated channel to prevent overlap with hurt sounds
        pygame.mixer.find_channel(True).play(self.player_death)


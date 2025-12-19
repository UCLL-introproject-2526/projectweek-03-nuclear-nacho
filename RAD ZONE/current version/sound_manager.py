import pygame
import random
import traceback

class SoundManager:
    def __init__(self):
        # Ensure mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # ---------------------- VOLUMES ----------------------
        WEAPON_VOLUME = 0.25
        ITEM_VOLUME = 0.4
        ZOMBIE_VOLUME = 0.5
        PLAYER_HURT_VOLUME = 0.5
        PLAYER_DEATH_VOLUME = 0.5

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
                "equip": pygame.mixer.Sound("RAD ZONE/current version/MP3/equip_revolver.mp3"),
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

        # Set weapon volumes
        for weapon_actions in self.weapon.values():
            for sound in weapon_actions.values():
                if sound:
                    sound.set_volume(WEAPON_VOLUME)

        # ---------------------- ITEM SOUNDS ----------------------
        self.items = {
            "pickup_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_bandages.mp3"),
            "pickup_iodine_pills": pygame.mixer.Sound("RAD ZONE/current version/MP3/pickup_iodine_pills.mp3"),
            "use_bandage": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_bandages.mp3"),
            "use_iodine": pygame.mixer.Sound("RAD ZONE/current version/MP3/use_iodine_pills.mp3"),
        }
        for sound in self.items.values():
            sound.set_volume(ITEM_VOLUME)

        # ---------------------- ZOMBIE DEATH SOUNDS ----------------------
        self.zombie_death = [
            pygame.mixer.Sound(f"RAD ZONE/current version/MP3/zomdie_die_{i}.mp3") 
            for i in range(1, 17)
        ]
        for sound in self.zombie_death:
            sound.set_volume(ZOMBIE_VOLUME)

        # ---------------------- PLAYER HURT & DEATH ----------------------
        self.player_hurt = [
            pygame.mixer.Sound(f"RAD ZONE/current version/MP3/player_take_damage_{i}.mp3") 
            for i in range(1, 6)
        ]
        for sound in self.player_hurt:
            sound.set_volume(PLAYER_HURT_VOLUME)
        self._player_hurt_index = 0
        self._player_hurt_channel = pygame.mixer.Channel(31)

        self.player_death = pygame.mixer.Sound("RAD ZONE/current version/MP3/scream_wilhelm.mp3")
        self.player_death.set_volume(PLAYER_DEATH_VOLUME)

        # ---------------------- DEDICATED CHANNELS ----------------------
        pygame.mixer.set_num_channels(64)  # or at least 34
        self._channels = {
            "weapon": pygame.mixer.Channel(30),
            "item": pygame.mixer.Channel(32),
            "zombie": pygame.mixer.Channel(33),
            "player_death": pygame.mixer.Channel(34),
        }

        # Track current equip sound to stop if needed
        self._current_equip_sound = None

    # ---------------------- WEAPON ----------------------
    def play_weapon(self, weapon, action):
        sound = self.weapon.get(weapon, {}).get(action)
        if not sound:
            return
        if action == "equip":
            if self._current_equip_sound and self._channels["weapon"].get_busy():
                self._channels["weapon"].stop()
            self._current_equip_sound = sound
        self._channels["weapon"].play(sound)


    # def play_weapon(self, weapon, action):
    #     print(f"\n[WEAPON SOUND] {weapon} -> {action}")
    #     traceback.print_stack(limit=6)
    #     return  # 🔇 keep silent


    # ---------------------- ITEM ----------------------
    def play_item(self, item_name):
        sound = self.items.get(item_name)
        if sound:
            self._channels["item"].play(sound)

    # ---------------------- ZOMBIE ----------------------
    def play_zombie_death(self):
        sound = random.choice(self.zombie_death)
        self._channels["zombie"].play(sound)

    # ---------------------- PLAYER HURT ----------------------
    def play_player_hurt(self):
        if not self._player_hurt_channel.get_busy():
            sound = self.player_hurt[self._player_hurt_index]
            self._player_hurt_channel.play(sound)
            self._player_hurt_index = (self._player_hurt_index + 1) % len(self.player_hurt)

    # ---------------------- PLAYER DEATH ----------------------
    def play_player_death(self):
        self._channels["player_death"].play(self.player_death)

class Weapon:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound

        # ---- FIRE MODE ----
        self.full_auto = (name == "rifle")       # Rifle is full-auto
        self.fire_rate = 0.15 if self.full_auto else 0.3  # seconds per shot
        self._last_shot_time = 0

    def equip(self):
        self.sound.play_weapon(self.name, "equip")

    def shoot(self, current_time):
        # Only fire if enough time has passed
        if current_time - self._last_shot_time < self.fire_rate:
            return False  # No shot fired → no sound

        self._last_shot_time = current_time
        self.sound.play_weapon(self.name, "shoot")  # Only when shot actually fires
        return True

    def reload(self):
        self.sound.play_weapon(self.name, "reload")

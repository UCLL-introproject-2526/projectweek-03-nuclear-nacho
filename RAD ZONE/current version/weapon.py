class Weapon:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound

        # ---- FIRE MODE ----
        self.full_auto = (name == "rifle")       # Rifle is full-auto
        self.fire_rate = 0.15 if self.full_auto else 0.3  # seconds per shot
        self._last_shot_time = 0

        # ---- DAMAGE, RANGE & WIDTH ----
        weapon_stats = {
            "pistol": {"damage": 25, "range": 800, "width": 40},
            "rifle": {"damage": 35, "range": 1200, "width": 30},
            "shotgun": {"damage": 60, "range": 400, "width": 60},
            "revolver": {"damage": 40, "range": 900, "width": 40},
            "crossbow": {"damage": 50, "range": 1000, "width": 30},
            "knife": {"damage": 50, "range": 100, "width": 20}  # melee
        }

        stats = weapon_stats.get(name, {"damage": 10, "range": 500, "width": 50})
        self.damage = stats["damage"]
        self.range = stats["range"]
        self.width = stats["width"]  # ✅ add this

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

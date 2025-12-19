class Weapon:
    def __init__(self, name, sound_manager):
        self.name = name
        self.sound_manager = sound_manager   # ✅ fix here

        self.full_auto = (name == "rifle")
        self.fire_rate = 0.15 if self.full_auto else 0.3
        self._last_shot_time = 0

        weapon_stats = {
            "pistol": {"damage": 25, "range": 800, "width": 40},
            "rifle": {"damage": 35, "range": 1200, "width": 30},
            "shotgun": {"damage": 60, "range": 400, "width": 60},
            "revolver": {"damage": 40, "range": 900, "width": 40},
            "crossbow": {"damage": 50, "range": 1000, "width": 30},
            "knife": {"damage": 50, "range": 100, "width": 20},
        }

        stats = weapon_stats.get(name)
        self.damage = stats["damage"]
        self.range = stats["range"]
        self.width = stats["width"]


    def equip(self):
        pass  # 🔇 intentionally silent

    # def shoot(self, current_time):
    #     if current_time - self._last_shot_time < self.fire_rate:
    #         return False

    def shoot(self, current_time):
        if current_time - self._last_shot_time < self.fire_rate:
            return False
        self._last_shot_time = current_time
        print(f"Firing {self.name}")  # 🔥 Debug line
        self.sound_manager.play_weapon(self.name, "shoot")
        return True

        self._last_shot_time = current_time
        return True  # still fires logically, just no sound

    def reload(self):
        pass  # 🔇 intentionally silent

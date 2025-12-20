class Weapon:
    def __init__(self, name, sound_manager):
        self.name = name
        self.sound_manager = sound_manager   # ✅ fix here

        self.full_auto = (name == "rifle")
        self.fire_rate = 0.15 if self.full_auto else 0.3
        self._last_shot_time = 0

        weapon_stats = {
            "knife": {"damage": 50, "range": 50, "fire_rate": 1.0, "width": 10},
            "pistol": {"damage": 20, "range": 300, "fire_rate": 0.5, "width": 15},
            "rifle": {"damage": 35, "range": 500, "fire_rate": 0.3, "width": 20},
            "revolver": {"damage": 30, "range": 300, "fire_rate": 0.6, "width": 18},
            "shotgun": {"damage": 70, "range": 100, "fire_rate": 1.0, "width": 25},
            "crossbow": {"damage": 40, "range": 400, "fire_rate": 1.2, "width": 20},
            "machine gun": {"damage": 30, "range": 300, "fire_rate": 0.02, "width": 22}  # ✅ Add all required keys 
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
        # print(f"Firing {self.name}")  # 🔥 Debug line
        self.sound_manager.play_weapon(self.name, "shoot")
        return True

        self._last_shot_time = current_time
        return True  # still fires logically, just no sound

    def reload(self):
        pass  # 🔇 intentionally silent

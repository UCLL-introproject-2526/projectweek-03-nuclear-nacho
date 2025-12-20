class Weapon:
    def __init__(self, id, sound_manager):
        self.id = id                  # the ID string like "shotgun"
        self.name = id                # optional, keep for display if needed
        self.sound_manager = sound_manager

        weapon_stats = {
            "knife": {
                "damage": 50,
                "range": 100,
                "fire_rate": 1.0,
                "width": 40,
                "full_auto": False
            },
            "pistol": {
                "damage": 20,
                "range": 400,
                "fire_rate": 0.1,
                "width": 20,
                "full_auto": False
            },
            "revolver": {
                "damage": 30,
                "range": 500,
                "fire_rate": 0.1,
                "width": 22,
                "full_auto": False
            },
            "shotgun": {
                "damage": 12,        # damage PER pellet
                "range": 400,
                "fire_rate": 0.8,
                "width": 35,
                "full_auto": False,
                "pellets": 6,        # 👈 ADD THIS
                "spread": 18         # 👈 ADD THIS (degrees)
            },
            "crossbow": {
                "damage": 60,
                "range": 600,
                "fire_rate": 1.2,
                "width": 18,
                "full_auto": False
            },
            "machine_gun": {
                "damage": 15,
                "range": 600,
                "fire_rate": 0.1,   # fast but stable
                "width": 22,
                "full_auto": True
            }
        }

        if id not in weapon_stats:
            raise ValueError(f"Unknown weapon id: {id}")

        stats = weapon_stats[id]

        # after loading stats:
        self.damage = stats["damage"]
        self.range = stats["range"]
        self.fire_rate = stats["fire_rate"]
        self.width = stats["width"]
        self.full_auto = stats["full_auto"]

        # Optional, shotgun-only
        self.pellets = stats.get("pellets", 1)
        self.spread = stats.get("spread", 0)

        self._last_shot_time = 0



    def equip(self):
        pass  # 🔇 intentionally silent

    # def shoot(self, current_time):
    #     if current_time - self._last_shot_time < self.fire_rate:
    #         return False

    def shoot(self, current_time):
        if current_time - self._last_shot_time >= self.fire_rate:
            self._last_shot_time = current_time
            return True
        return False


    def reload(self):
        pass  # 🔇 intentionally silent

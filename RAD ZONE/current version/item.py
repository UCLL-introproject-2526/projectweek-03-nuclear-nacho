class Item:
    def __init__(self, item_id, icon_surf, weapon_surf):
        self._id = item_id
        self._icon = icon_surf
        self._weapon = weapon_surf
        self._rect = self._icon.get_rect()

    # --- getters ---
    def get_id(self):
        return self._id

    def get_icon(self):
        return self._icon

    def get_weapon_surface(self):
        return self._weapon

    def get_rect(self):
        return self._rect

    # --- logic ---
    def set_position(self, pos):
        self._rect.center = pos

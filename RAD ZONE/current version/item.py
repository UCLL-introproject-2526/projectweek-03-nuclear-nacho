class Item:
    def __init__(self, item_id, icon_surf, weapon_surf=None,
                 stackable=False, amount=1, max_stack=1):

        self._id = item_id
        self._icon = icon_surf
        self._weapon = weapon_surf

        self._stackable = stackable
        self._amount = amount
        self._max_stack = max_stack

        self._rect = self._icon.get_rect()

    # --- getters ---
    def get_id(self):
        return self._id

    def get_icon(self):
        return self._icon

    def get_weapon_surface(self):
        return self._weapon

    def is_stackable(self):
        return self._stackable

    def get_amount(self):
        return self._amount

    def get_max_stack(self):
        return self._max_stack

    # --- stack logic ---
    def can_stack_with(self, other):
        return (
            other
            and self._stackable
            and other.get_id() == self._id
            and other.get_amount() < other.get_max_stack()
        )

    def add_to_stack(self, amount):
        space = self._max_stack - self._amount
        added = min(space, amount)
        self._amount += added
        return added

    def remove_from_stack(self, amount):
        self._amount -= amount
        return self._amount <= 0

    # --- logic ---
    def set_position(self, pos):
        self._rect.center = pos
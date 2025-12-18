class UI:
    def __init__(self, health, stamina, outline):
        self._health = health
        self._stamina = stamina
        self._outline = outline

    def draw(self, screen, health_value, max_health=100):
        """Draw single health bar using health_value"""
        ratio = health_value / max_health
        ratio = max(0, min(ratio, 1))

        # Get the position from the rect
        bar_pos = self._health[1].topleft
        
        # Draw background (full bar) first
        screen.blit(self._health[0], bar_pos)
        
        # Draw filled portion on top
        if ratio > 0:
            width = int(self._health[0].get_width() * ratio)
            part = self._health[0].subsurface(
                (0, 0, width, self._health[0].get_height())
            )
            screen.blit(part, bar_pos)

        # Draw outline on top
        screen.blit(self._outline[0], bar_pos)
    
    def draw_health(self, screen, health_value, max_health):
        """Compatibility method - calls draw"""
        self.draw(screen, health_value, max_health)

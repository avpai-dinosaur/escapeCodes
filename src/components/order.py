"""
order.py
"""

import pygame
import src.core.utils as utils
import src.constants as c

class OrderUi:
    def __init__(self, width):
        self.width = width
        self.textMargin = 10
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)
        self.infoIcon, self.infoIconRect = utils.load_png("information.png")
        # Event Subscribers
        EventManager.subscribe(EcodeEvent.PLAYER_MOVED, self.on_player_move)

    def on_player_move(self, **kwargs):
        self.disappearStartTimestamp = pygame.time.get_ticks()
        EventManager.unsubscribe(EcodeEvent.PLAYER_MOVED, self.on_player_move)

    
    def set_text(self, text: str):
        self.textImage = self.font.render(text, True, "white", wraplength=self.width - 2 * self.textMargin)
        self.textRect = self.textImage.get_rect()
        self.rect = self.textRect.inflate(self.textMargin * 2, self.textMargin * 2)
        self.rect.top = 10
        self.rect.right = c.SCREEN_WIDTH - 10
        self.textRect.top = self.rect.top + self.textMargin
        self.textRect.left = self.rect.left + self.textMargin
        self.infoIconRect.bottomright = self.rect.bottomright
        self.startVisibility = pygame.time.get_ticks()
        self.isVisible = True
    
    def update(self):
        if pygame.time.get_ticks() - self.startVisibility > 10000:
            self.isVisible = False

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, "dimgrey", self.rect, border_radius=5)
            surface.blit(self.textImage, self.textRect)
            surface.blit(self.infoIcon, self.infoIconRect)
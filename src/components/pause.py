"""
pause.py
"""

import pygame
import src.core.utils as utils
import src.constants as c
from src.core.ecodeEvents import EventManager, EcodeEvent

class PauseUi:
    def __init__(self):
        """Constructor."""
        self.settingIcon, _ = utils.load_png("settingsIcon.png")
        self.settingIcon = pygame.transform.scale(self.settingIcon, (24, 24))
        settingWidth, settingHeight = self.settingIcon.get_size()
        self.settingRect = pygame.Rect(0,0, settingWidth, settingHeight)
        self.settingIconRect = self.settingIcon.get_rect(topleft=(5,5))
        
    def handle_event(self, event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if utils.is_mouse_in_rect(self.settingIconRect):
                EventManager.emit(EcodeEvent.PAUSE_MENU)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.settingIcon, self.settingIconRect)
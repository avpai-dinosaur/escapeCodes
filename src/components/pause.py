"""
pause.py
"""

import pygame
import src.core.utils as utils
import src.constants as c
from src.core.ecodeEvents import EventManager, EcodeEvent

class PauseUi:
    def __init__(self):
        #pause menu setup
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


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("Scrollable")
    clock = pygame.time.Clock()
   

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            PauseUi.handle_event(event)

        #orderUi.update()
        
        screen.fill("black")
        PauseUi.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        #WHATS THE PURPOSE OF THIS PART IF ITS ALL IN UI MANAGER?
    
    pygame.quit()
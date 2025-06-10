"""
order.py
"""

import pygame
import src.core.utils as utils
import src.constants as c
from src.core.ecodeEvents import EventManager, EcodeEvent

class OrderUi:
    def __init__(self, width):
        self.width = width
        self.textMargin = 10
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)
        #info setup
        self.infoIcon, self.infoIconRect = utils.load_png("information.png")
        self.on_give_order("")
        self.isVisible = False
        
        #pause menu setup
        self.settingIcon, _ = utils.load_png("settingsIcon.png")
        self.settingIcon = pygame.transform.scale(self.settingIcon, (36, 36))
        settingWidth, settingHeight = self.settingIcon.get_size()
        self.settingRect = pygame.Rect(0,0, settingWidth, settingHeight)
        self.settingIconRect = self.settingIcon.get_rect(topleft=(5,5))
        # Event Subscribers
        EventManager.subscribe(EcodeEvent.GIVE_ORDER, self.on_give_order)

    def on_give_order(self, text: str):
        self.startVisibility = pygame.time.get_ticks()
        self.set_text(text)

    def set_text(self, text: str):
        self.textImage = self.font.render(text, True, "white", wraplength=self.width - 2 * self.textMargin)
        self.textRect = self.textImage.get_rect()
        self.rect = pygame.Rect()
        self.rect.width = self.textMargin + self.textRect.width + self.infoIconRect.width
        self.rect.height = self.textRect.height + self.textMargin * 2
        self.rect.top = 10
        self.rect.right = c.SCREEN_WIDTH - 10
        self.textRect.top = self.rect.top + self.textMargin
        self.textRect.left = self.rect.left + self.textMargin
        self.infoIconRect.topright = self.rect.topright
        self.startVisibility = pygame.time.get_ticks()
        self.isVisible = True
    
    def update(self):
        if self.startVisibility and pygame.time.get_ticks() - self.startVisibility > 10000:
            self.isVisible = False

    def handle_event(self, event: pygame.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if utils.is_mouse_in_rect(self.infoIconRect):
                if not self.isVisible:
                    self.startVisibility = pygame.time.get_ticks()
                self.isVisible = not self.isVisible
            if utils.is_mouse_in_rect(self.settingIconRect):
                print("buttong is working!")
                #self.manager.set_state("pause")

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, "dimgrey", self.rect, border_radius=5)
            surface.blit(self.textImage, self.textRect)
        surface.blit(self.infoIcon, self.infoIconRect)
        surface.blit(self.settingIcon, self.settingIconRect)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("Scrollable")
    clock = pygame.time.Clock()

    orderUi = OrderUi(c.SCREEN_WIDTH // 5)
    orderUi.set_text("Hello this is an order for you")    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            orderUi.handle_event(event)

        orderUi.update()
        
        screen.fill("black")
        orderUi.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
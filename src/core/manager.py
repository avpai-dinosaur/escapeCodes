import pygame
from src.core.game import Game
from src.core.leetcodeManager import LeetcodeManager
from src.components.menu import MainMenu, OptionsMenu, LoginMenu, YouDiedMenu
import src.core.utils as utils
import src.constants as c

class GameManager:
    def __init__(self):
        self.states = {
            "menu": MainMenu,
            "options": OptionsMenu,
            "login": LoginMenu,
            "intro": TextSlideShow,
            "world": Game,
            "died": YouDiedMenu
        }
        self.set_state("menu")
        self.leetcodeManager = LeetcodeManager()

    def set_state(self, state_name):
        pygame.display.set_caption(state_name)
        self.activeState = self.states[state_name](self) # Call the state's constructor

    def handle_event(self, event):
        self.activeState.handle_event(event)
        self.leetcodeManager.handle_event(event)

    def update(self):
        self.activeState.update()

    def draw(self, screen):
        self.activeState.draw(screen)

class TextSlideShow:
    def __init__(self, manager):
        """Constructor."""
        self.manager = manager
        self.lines = [
"""2032:
First permanent colony and fully-automated mining venture established on Mars by tech conglomerate WeX.
A bidding war for prime real estate begins amongst the company's top executives.""",
"""2035:
The universe's most incredible travel destinations are unlocked.
The Utopia, an one-of-a-kind vessel, announces its passage from Earth to Mars, intended to host neo-settlers and start-ups alike.""",
"""2041:
The Earth bleeds, wrought by man-made fires, crumbling infrastructure, and worn reserves of nearly everything needed to sustain human life.
There are no more resources: a planet in revolt. It is time to go.""",
"""2042 (Present):
You are a technician tasked with checking the Utopia before the expedition, preparing for an unforgettable trip to the New World.""" 
        ]
        self.line = 0
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)
        self.font2 = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)
        self.margin = 100
        self.render_text()
    
    def render_text(self):        
        self.textImage = self.font.render(
            self.lines[self.line],
            True,
            "white",
            wraplength=c.SCREEN_WIDTH - 2 * self.margin
        )
        self.textRect = self.textImage.get_rect()
        self.textRect.centerx = c.SCREEN_WIDTH // 2
        self.textRect.centery = c.SCREEN_HEIGHT // 2

        self.textImage2 = self.font2.render(
            '\nPress Return to Continue',
            True,
            "white",
            wraplength=c.SCREEN_WIDTH - 2 * self.margin
        )
        self.textRect2 = self.textImage2.get_rect()
        self.textRect2.centerx = c.SCREEN_WIDTH // 2
        self.textRect2.centery = c.SCREEN_HEIGHT // 2 + 150

    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.line += 1
                if self.line >= len(self.lines):
                    self.manager.set_state("world")
                else:
                    self.render_text()
    
    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.textImage, self.textRect)
        screen.blit(self.textImage2, self.textRect2)
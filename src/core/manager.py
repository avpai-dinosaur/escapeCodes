import pygame
from src.core.game import Game
from src.core.leetcodeManager import LeetcodeManager
from src.components.menu import MainMenu, OptionsMenu, LoginMenu, YouDiedMenu
import src.core.utils as utils
import src.constants as c

class GameManager:
    def __init__(self):
        self.states = {
            "menu": MainMenu(self),
            "options": OptionsMenu(self),
            "login": LoginMenu(self),
            "intro": TextSlideShow(self),
            "world": Game(self, {}),
            "died": YouDiedMenu(self)
        }
        self.active_state = self.states["menu"]
        self.leetcodeManager = LeetcodeManager()

    def set_state(self, state_name):
        pygame.display.set_caption(state_name)
        self.active_state = self.states[state_name]

    def handle_event(self, event):
        self.active_state.handle_event(event)
        self.leetcodeManager.handle_event(event)

    def update(self):
        self.active_state.update()

    def draw(self, screen):
        self.active_state.draw(screen)

class TextSlideShow:
    def __init__(self, manager):
        """Constructor."""
        self.manager = manager
        self.lines = [
            "2032\nFirst automated colony established on Mars by tech conglomerate WeX.",
            "2035\nPrime real estate becomes available for purchase.",
            "2040\nThe universe's most incredible travel destinations are unlocked; the Utopia, a one-of-a-kind vessel, announces its passage from Earth to Mars, hosting neo-settlers and start-ups alike.",
            "2042\nNow...You are the latest recruit for the expedition, preparing for an unforgettable trip to the New World."
        ]
        self.line = 0
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)
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
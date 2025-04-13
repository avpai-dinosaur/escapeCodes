import pygame
from src.core.game import Game
from src.components.menu import MainMenu, OptionsMenu, LoginMenu, YouDiedMenu

class GameManager:
    def __init__(self):
        self.states = {
            "menu": MainMenu(self),
            "options": OptionsMenu(self),
            "login": LoginMenu(self),
            "world": Game(self, {}),
            "died": YouDiedMenu(self)
        }
        self.active_state = self.states["menu"]

    def set_state(self, state_name):
        pygame.display.set_caption(state_name)
        self.active_state = self.states[state_name]

    def handle_event(self, event):
        self.active_state.handle_event(event)

    def update(self):
        self.active_state.update()

    def draw(self, screen):
        self.active_state.draw(screen)
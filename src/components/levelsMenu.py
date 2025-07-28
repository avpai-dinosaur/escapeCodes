import pygame
import sys
import requests
import json
from pprint import pprint
import src.core.utils as utils
import src.config as config
import src.constants as c
from src.components.button import Button, TextInput, ToggleButton
from src.components.ui import KeyPromptControlBarUi, KeyPromptUi
from src.components.menu import Menu

class LevelsMenu(Menu):
    """Levels Menu"""
    def __init__(self, manager):
        super().__init__(manager)
        self.playImage, _ = utils.load_png("Play.png")
        self.backImage, _ = utils.load_png("Play.png")
        self.headingFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)
        self.controls += [
            Button(self.playImage, pos=(1000, 300), textInput="Play", onClick=self.onPlay),
            Button(self.backImage, pos=(1000, 540), textInput="Back", onClick=self.onBack)
        ]
        self.backImageRect = self.backImage.get_rect(center=(1000, 540))

       
       
    def update(self):
        super().update()

    def onPlay(self):
        self.manager.set_state("world")

    def onBack(self):
        self.manager.set_state("menu")

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        
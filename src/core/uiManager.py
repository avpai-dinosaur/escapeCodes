import pygame
from src.core.ecodeEvents import EcodeEvent
from src.components import ui

class UiManager:
    def __init__(self):
        self.wasdUi = ui.WasdUi((10, 10))
        self.noteUi = ui.NoteUi()
    
    def handle_event(self, event):
        self.noteUi.handle_event(event)

    def update(self):
        self.wasdUi.update()
        self.noteUi.update()

    def draw(self, surface):
        self.wasdUi.draw(surface)
        self.noteUi.draw(surface)
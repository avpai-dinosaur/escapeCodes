import pygame
from src.components import ui

class UiManager:
    def __init__(self):
        self.wasdUi = ui.WasdUi(pygame.Vector2(10, 10))
        self.noteUi = ui.NoteUi()
        self.movingBarUi = ui.MovingBarUi()
    
    def handle_event(self, event):
        self.noteUi.handle_event(event)
        self.movingBarUi.handle_event(event)

    def update(self):
        self.wasdUi.update()
        self.noteUi.update()
        self.movingBarUi.update()

    def draw(self, surface):
        self.wasdUi.draw(surface)
        self.noteUi.draw(surface)
        self.movingBarUi.draw(surface)
import pygame
from src.components import ui

class UiManager:
    def __init__(self):
        self.wasdUi = ui.WasdUi(pygame.Vector2(10, 10))
        self.noteUi = ui.NoteUi()
        self.testCaseBattleUi = ui.TestCaseHackUi()
        self.movingBarUi = ui.MovingBarUi()
        self.dialogUi = ui.DialogUi()
        self.pinUi = ui.PinPad()
    
    def handle_event(self, event):
        self.noteUi.handle_event(event)
        self.movingBarUi.handle_event(event)
        self.testCaseBattleUi.handle_event(event)
        self.dialogUi.handle_event(event)
        self.pinUi.handle_event(event)

    def update(self):
        self.wasdUi.update()
        self.noteUi.update()
        self.movingBarUi.update()
        self.testCaseBattleUi.update()
        self.pinUi.update()

    def draw(self, surface):
        self.wasdUi.draw(surface)
        self.noteUi.draw(surface)
        self.movingBarUi.draw(surface)
        self.testCaseBattleUi.draw(surface)
        self.dialogUi.draw(surface)
        self.pinUi.draw(surface)
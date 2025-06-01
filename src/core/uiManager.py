import pygame
from src.components import ui
from src.components import order, note
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.constants as c

class UiManager:
    def __init__(self):
        self.wasdUi = ui.WasdUi(pygame.Vector2(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 200))
        self.testCaseBattleUi = ui.TestCaseHackUi()
        self.movingBarUi = ui.MovingBarUi()
        self.dialogUi = ui.DialogUi()
        self.pinUi = ui.PinPad()
        self.orderUi = order.OrderUi(500)

        self.activeUi = set()

        EventManager.subscribe(EcodeEvent.OPEN_NOTE, self.on_open_note)

    def on_open_note(self, text: str, url: str=None, isSolved: bool=False, pinText: str=""):
        noteUi = note.NoteUi(self.deactivate_ui)
        noteUi.set_text(text, url, isSolved, pinText)
        self.activeUi.add(noteUi)
    
    def deactivate_ui(self, uiElement):
        if uiElement in self.activeUi:
            self.activeUi.remove(uiElement)

    def handle_event(self, event):
        for ui in self.activeUi.copy():
            ui.handle_event(event)
        self.movingBarUi.handle_event(event)
        self.testCaseBattleUi.handle_event(event)
        self.dialogUi.handle_event(event)
        self.pinUi.handle_event(event)
        self.orderUi.handle_event(event)

    def update(self):
        for ui in self.activeUi.copy():
            ui.update()
        self.wasdUi.update()
        self.movingBarUi.update()
        self.testCaseBattleUi.update()
        self.pinUi.update()
        self.orderUi.update()

    def draw(self, surface):
        for ui in self.activeUi.copy():
            ui.draw(surface)
        self.wasdUi.draw(surface)
        self.movingBarUi.draw(surface)
        self.testCaseBattleUi.draw(surface)
        self.dialogUi.draw(surface)
        self.pinUi.draw(surface)
        self.orderUi.draw(surface)
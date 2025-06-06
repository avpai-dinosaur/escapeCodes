import pygame
from src.components import ui
from src.components import order, note
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.constants as c

class UiManager:
    def __init__(self):
        self.testCaseBattleUi = ui.TestCaseHackUi()
        self.movingBarUi = ui.MovingBarUi()
        self.pinUi = ui.PinPad()
        self.orderUi = order.OrderUi(500)

        self.activeUi = set()

        EventManager.subscribe(EcodeEvent.OPEN_NOTE, self.on_open_note)
        EventManager.subscribe(EcodeEvent.OPEN_KEY_PROMPT, self.on_open_key_prompt)
        EventManager.subscribe(EcodeEvent.OPEN_WASD, self.on_open_wasd)
        EventManager.subscribe(EcodeEvent.OPEN_DIALOG, self.on_open_dialog)

    def on_open_note(self, text: str, url: str=None, isSolved: bool=False, pinText: str=""):
        noteUi = note.NoteUi(self.deactivate_ui)
        noteUi.set_text(text, url, isSolved, pinText)
        self.activeUi.add(noteUi)
    
    def on_open_key_prompt(self, key, filename, fileMetadata=c.SM_KEY_SHEET_METADATA, caption=""):
        keyPromptUi = ui.StandAloneKeyPromptUi(
            self.deactivate_ui,
            key, filename,
            fileMetadata=fileMetadata,
            caption=caption
        )
        keyPromptUi.rect.center = pygame.Vector2(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 200)
        self.activeUi.add(keyPromptUi)
    
    def on_open_wasd(self):
        wasdUi = ui.WasdUi(
            self.deactivate_ui,
            pygame.Vector2(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 200)
        )
        self.activeUi.add(wasdUi)

    def on_open_dialog(self, lines: list[str], currentLine: int):
        EventManager.emit(EcodeEvent.PAUSE_GAME)
        dialog = ui.DialogUi(self.deactivate_ui, lines, currentLine)
        self.activeUi.add(dialog)
        
    def deactivate_ui(self, uiElement):
        if uiElement in self.activeUi:
            self.activeUi.remove(uiElement)

    def handle_event(self, event):
        for ui in self.activeUi.copy():
            ui.handle_event(event)
        self.movingBarUi.handle_event(event)
        self.testCaseBattleUi.handle_event(event)
        self.pinUi.handle_event(event)
        self.orderUi.handle_event(event)

    def update(self):
        for ui in self.activeUi.copy():
            ui.update()
        self.movingBarUi.update()
        self.testCaseBattleUi.update()
        self.pinUi.update()
        self.orderUi.update()

    def draw(self, surface):
        for ui in self.activeUi.copy():
            ui.draw(surface)
        self.movingBarUi.draw(surface)
        self.testCaseBattleUi.draw(surface)
        self.pinUi.draw(surface)
        self.orderUi.draw(surface)
import pygame
from src.components import ui
from src.components import order, note, hack, pause
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.constants as c

class UiManager:
    def __init__(self):
        # TODO: Move these into activeUi
        self.movingBarUi = ui.MovingBarUi()
        self.pinUi = ui.PinPad()
        self.orderUi = order.OrderUi(500)
        self.pauseUi = pause.PauseUi()
        self.activeUi = set()
        self.uiMap = dict()

        EventManager.subscribe(EcodeEvent.OPEN_NOTE, self.on_open_note)
        EventManager.subscribe(EcodeEvent.OPEN_KEY_PROMPT, self.on_open_key_prompt)
        EventManager.subscribe(EcodeEvent.OPEN_WASD, self.on_open_wasd)
        EventManager.subscribe(EcodeEvent.OPEN_DIALOG, self.on_open_dialog)
        EventManager.subscribe(EcodeEvent.BOSS_HACK, self.on_open_hack)

    def on_open_note(self, text: str, url: str=None, isSolved: bool=False, pinText: str=""):
        noteUi = note.NoteUi(self.deactivate_ui)
        noteUi.set_text(text, url, isSolved, pinText)
        self.uiMap[note.NoteUi] = noteUi
    
    def on_open_key_prompt(self, key, filename, fileMetadata=c.SM_KEY_SHEET_METADATA, caption=""):
        keyPromptUi = ui.StandAloneKeyPromptUi(
            self.deactivate_ui,
            key, filename,
            fileMetadata=fileMetadata,
            caption=caption
        )
        keyPromptUi.rect.center = pygame.Vector2(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 200)
        self.uiMap[ui.StandAloneKeyPromptUi] = keyPromptUi
    
    def on_open_wasd(self):
        wasdUi = ui.WasdUi(
            self.deactivate_ui,
            pygame.Vector2(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 200)
        )
        self.uiMap[ui.WasdUi] = wasdUi

    def on_open_dialog(self, lines: list[str], currentLine: int):
        EventManager.emit(EcodeEvent.PAUSE_GAME)
        dialog = ui.DialogUi(self.deactivate_ui, lines, currentLine)
        self.uiMap[ui.DialogUi] = dialog
    
    def on_open_hack(self, problemSlug: str):
        hackUi = hack.TestCaseHackUi(self.deactivate_ui, problemSlug)
        self.uiMap[hack.TestCaseHackUi] = hackUi
        
    def deactivate_ui(self, uiType):
        if uiType in self.uiMap:
            del self.uiMap[uiType]

    def handle_event(self, event):
        for ui in self.uiMap.copy().values():
            ui.handle_event(event)
        self.movingBarUi.handle_event(event)
        self.pinUi.handle_event(event)
        self.orderUi.handle_event(event)
        self.pauseUi.handle_event(event)

    def update(self):
        for ui in self.uiMap.copy().values():
            ui.update()
        self.movingBarUi.update()
        self.pinUi.update()
        self.orderUi.update()

    def draw(self, surface):
        for ui in self.uiMap.copy().values():
            ui.draw(surface)
        self.movingBarUi.draw(surface)
        self.pinUi.draw(surface)
        self.orderUi.draw(surface)
        self.pauseUi.draw(surface)
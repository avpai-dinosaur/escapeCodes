import pygame
from src.components import ui
from src.components import order
import src.constants as c

class UiManager:
    def __init__(self):
        self.wasdUi = ui.WasdUi(pygame.Vector2(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2 + 200))
        self.noteUi = ui.NoteUi()
        self.testCaseBattleUi = ui.TestCaseHackUi()
        self.movingBarUi = ui.MovingBarUi()
        self.dialogUi = ui.DialogUi()
        self.pinUi = ui.PinPad()
        self.orderUi = order.OrderUi(500)
        self.orderUi.set_text("Secure the bridge between our world and the Utopia. You are responsible for ensuring that it is in operational order before liftoff.")
        self.orderUi.rect.top = 10
        self.orderUi.rect.right = c.SCREEN_WIDTH - 10
    
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
        self.orderUi.update()

    def draw(self, surface):
        self.wasdUi.draw(surface)
        self.noteUi.draw(surface)
        self.movingBarUi.draw(surface)
        self.testCaseBattleUi.draw(surface)
        self.dialogUi.draw(surface)
        self.pinUi.draw(surface)
        self.orderUi.draw(surface)
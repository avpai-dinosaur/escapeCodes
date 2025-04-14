from src.components.ui import WasdUi
from src.components.ui import NoteUi

class UiManager:
    def __init__(self):
        self.wasdUi = WasdUi((10, 10))
        self.noteUi = NoteUi()
    
    def update(self):
        self.wasdUi.update()

    def draw(self, surface):
        self.wasdUi.draw(surface)
        self.noteUi.draw(surface)
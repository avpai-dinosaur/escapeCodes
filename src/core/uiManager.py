from src.components.ui import WasdUi
from src.components.ui import NoteUi

class UiManager:
    def __init__(self):
        self.wasdUi = WasdUi((10, 10))

        text = """From: Melon Husk
To: All
Subject: Bumping up efficiency.

Hey Technicians!
If you're looking at this note I'm guessing you noticed the giant laser door blocking the ship's main entrance. Perhaps you also noticed that we are behind on the launch schedule? Again! Honestly, I'm wondering if half of you guys can even code at this point.

Anyways, I've cooked up a little challenge to get us back on track. From now on, to get into the ship, you've got to solve a little coding problem called (412. Fizz Buzz).

Best Regards,
Melon
"""
        self.noteUi = NoteUi(text)
    
    def update(self):
        self.wasdUi.update()

    def draw(self, surface):
        self.wasdUi.draw(surface)
        self.noteUi.draw(surface)
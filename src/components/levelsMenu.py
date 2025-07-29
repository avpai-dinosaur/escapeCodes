import pygame
from pprint import pprint
import src.core.utils as utils
from src.components.button import Button, TriangleButton
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.components.menu import Menu

class LevelsMenu(Menu):
    """Levels Menu"""
    def __init__(self, manager):
        super().__init__(manager)
        self.playImage, _ = utils.load_png("Play.png")
        self.backImage, _ = utils.load_png("Play.png")
        self.headingFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)

        self.levels = [
            SelectLevel("Tutorial", "Keys/0-Key.png"),
            SelectLevel("Caves", "Keys/1-Key.png"),
            SelectLevel("Lab", "Keys/2-Key.png"),
            SelectLevel("Lab", "Keys/3-Key.png")
        ]
        self.currentIdx = 0

        self.right_arrow = self.create_right_triangle(center=(1000, 400), width=50, height=100)
        self.left_arrow = self.create_left_triangle(center=(280,400), width=50,height=100)
        self.color = (255, 0, 0)
        
        self.controls += [
            TriangleButton(self.right_arrow, onClick=self.onRight),
            TriangleButton(self.left_arrow, onClick=self.onLeft),
            Button(self.playImage, pos=(280, 660), textInput="Play", onClick=self.onPlay),
            Button(self.backImage, pos=(1000, 660), textInput="Back", onClick=self.onBack)
        ]
   
    def update(self):
        super().update()

    def onPlay(self):
        #self.manager.set_state("world")
        EventManager.emit(EcodeEvent.LOAD_LEVEL, self.currentIdx)

    def onBack(self):
        self.manager.set_state("menu")
    
    def onLeft(self):
        self.currentIdx = (self.currentIdx - 1) % len(self.levels)

    def onRight(self):
        self.currentIdx = (self.currentIdx + 1) % len(self.levels)

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        current_level = self.levels[self.currentIdx]
        surface.blit(current_level.image, current_level.image_rect)



    """Triangle Creation Should I move this into Triangle Button?"""
    def create_right_triangle(self, center: tuple[int, int], width: int, height: int) -> list[tuple[int, int]]:
        cx, cy = center
        half_height = height // 2

        p1 = (cx - width // 2, cy - half_height)  # top-left
        p2 = (cx - width // 2, cy + half_height)  # bottom-left
        p3 = (cx + width // 2, cy)                # right tip

        return [p1, p2, p3]
    
    def create_left_triangle(self, center: tuple[int, int], width: int, height: int) -> list[tuple[int, int]]:
        cx, cy = center
        half_height = height // 2

        p1 = (cx + width // 2, cy - half_height)  # top-right
        p2 = (cx + width // 2, cy + half_height)  # bottom-right
        p3 = (cx - width // 2, cy)                # left tip

        return [p1, p2, p3]

class SelectLevel:
    def __init__(self, name: str, image_path: str, description: str = "", difficulty: str = ""):
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.image, _ = utils.load_png(image_path)
        self.image_rect = self.image.get_rect(center=(640, 400))
    
    def draw(self, surface: pygame.Surface):
        super().draw(surface)


        
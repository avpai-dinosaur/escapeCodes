import pygame
import src.core.utils as utils
from src.components.button import Button
from src.components.menu import Menu
from src.core.gameStates import GameStates

class LevelsMenu(Menu):
    """Levels Menu"""
    def __init__(self, manager):
        super().__init__(manager)
        self.playImage, _ = utils.load_png("Play.png")
        self.backImage, _ = utils.load_png("Play.png")
        self.titleFont = utils.load_font("Monoton/Monoton-Regular.ttf", 60)
        self.titleTextImage = self.titleFont.render("Level Selection", True, "white")
        self.titleRect = self.titleTextImage.get_rect(center=(640, 150))

        self.levelFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 40)
        self.errorFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)

        self.levels = [
            SelectLevel("Tutorial", 0, "level0.png", False),
            SelectLevel("Caves", 1, "level1.png", True),
            SelectLevel("Lab", 2, "level2.png", True),
            SelectLevel("Boss", 3, "level3.png", True)
        ]

        self.currentIdx = 0
        self.errorTextImage = self.errorFont.render("The level is currently locked!", True, 'red')
        self.errorTextRect = self.errorTextImage.get_rect(center=(640, 600))
        self.showError = False
        self.error_start_time = None
        self.error_duration = 5000

        self.rightArrow = pygame.transform.invert(
            pygame.transform.scale(
                utils.load_png("rightArrow.png")[0],
                (150, 150)
            )
        )
        self.leftArrow = pygame.transform.flip(self.rightArrow, True, False)

        self.controls += [
            Button(self.rightArrow, pos=(1000, 400), textInput="", onClick=self.onRight),
            Button(self.leftArrow, pos=(280, 400), textInput="", onClick=self.onLeft),
            Button(self.playImage, pos=(280, 700), textInput="Play", onClick=self.onPlay),
            Button(self.backImage, pos=(1000, 700), textInput="Back", onClick=self.onBack)
        ]
        for i in range(0, self.manager.num_unlocked + 1):
            self.levels[i].locked = False
   
    def onPlay(self):
        current_level = self.levels[self.currentIdx]
        if(current_level.locked == False):
            self.manager.level_idx = self.currentIdx
            self.manager.set_state(GameStates.Game)
        else:
            self.showError = True
            self.error_start_time = pygame.time.get_ticks()
            
    def onBack(self):
        self.manager.set_state(GameStates.Menu)
    
    def onLeft(self):
        self.currentIdx = (self.currentIdx - 1) % len(self.levels)
        self.reset_error()

    def onRight(self):
        self.currentIdx = (self.currentIdx + 1) % len(self.levels)
        self.reset_error()

    def reset_error(self):
        self.showError = False
        self.error_start_time = None 

    def draw(self, surface: pygame.Surface):
        super().draw(surface)

        surface.blit(self.titleTextImage, self.titleRect)

        current_level = self.levels[self.currentIdx]
        surface.blit(current_level.image, current_level.image_rect)
        level_name = self.levelFont.render(current_level.name, True, "white")
        name_rect = level_name.get_rect(center=(640, 550))
        surface.blit(level_name, name_rect)

        if(current_level.locked):
            lockedImage, _ = utils.load_png("locked.png")
            self.scaled_image = pygame.transform.scale(lockedImage, (90, 128))
            self.lockedImage_rect = self.scaled_image.get_rect(center=(640,400))
            surface.blit(self.scaled_image, self.lockedImage_rect)

        if(self.showError and self.error_start_time):
            elapsed = pygame.time.get_ticks() - self.error_start_time
            if elapsed < self.error_duration:
                surface.blit(self.errorTextImage, self.errorTextRect)
            else:
                self.error_start_time = None

class SelectLevel:
    def __init__(self, name: str, idx: int, image_path: str, locked: bool, description: str = "", difficulty: str = ""):
        self.name = name
        self.idx = idx
        self.description = description
        self.difficulty = difficulty
        self.image = pygame.transform.scale(
            utils.load_png(image_path)[0],
            (500, 200)
        )
        self.image_rect = self.image.get_rect(center=(640, 400))
        self.locked = locked
    
    def draw(self, surface: pygame.Surface):
        super().draw(surface)


        
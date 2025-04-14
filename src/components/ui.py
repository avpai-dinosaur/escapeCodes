import pygame
from src.core.spritesheet import SpriteSheet
from src.core.ecodeEvents import EcodeEvent, EventManager
from src.core import utils
from src import constants as c

class WasdUi:
    """Class representing 'WASD to move' ui instruction."""

    def __init__(self, pos: pygame.Vector2):
        """Constructor.
        
            pos: Position of the ui instruction.
        """
        self.spritesheet = SpriteSheet("wasd.png", c.WASD_SHEET_METADATA)
        self.currentFrame = 0
        self.image = self.spritesheet.get_image("press", self.currentFrame)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.lastUpdate = pygame.time.get_ticks()
        self.isVisible = True
        self.disappearStartTimestamp = None

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.PLAYER_MOVED, self.on_player_move)

    def on_player_move(self, **kwargs):
        self.disappearStartTimestamp = pygame.time.get_ticks()
        EventManager.unsubscribe(EcodeEvent.PLAYER_MOVED, self.on_player_move)

    def update(self):
        if pygame.time.get_ticks() - self.lastUpdate >= self.spritesheet.cooldown("press"):
            self.currentFrame += 1
            if self.currentFrame == self.spritesheet.num_frames("press"):
                self.currentFrame = 0
            self.image = self.spritesheet.get_image("press", self.currentFrame)
            self.lastUpdate = pygame.time.get_ticks()

        if self.disappearStartTimestamp is not None:
            if pygame.time.get_ticks() - self.disappearStartTimestamp >= 3000:
                self.isVisible = False
    
    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            surface.blit(self.image, self.rect)

class NoteUi:
    def __init__(self, text: str):
        """Constructor.
        
            text: Text to display on note.
        """
        self.padding = 20
        self.backgroundRect = pygame.Rect()
        self.backgroundRect.width = c.SCREEN_WIDTH - 2 * self.padding
        self.backgroundRect.height = c.SCREEN_HEIGHT - 2 * self.padding
        self.backgroundRect.topleft = (self.padding, self.padding)

        self.innerTextMargin = 10
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)
        self.noteTextImage = self.font.render(text, True, 'white', wraplength=self.backgroundRect.width - 2 * self.innerTextMargin)
        self.noteTextRect = self.noteTextImage.get_rect()
        self.noteTextRect.topleft = (self.padding + self.innerTextMargin, self.padding + self.innerTextMargin)
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
        surface.blit(self.noteTextImage, self.noteTextRect)


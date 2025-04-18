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

class KeyUi:
    """Class representing 'press key' prompt animation."""

    def __init__(
        self,
        key: int,
        filename: str,
        pos: pygame.Vector2
    ):
        """Constructor.
        
            key: The key (e.g. pygame.K_m).
            filename: The key spritesheet.
            pos: Position of the ui element.
        """
        self.key = key
        self.spritesheet = SpriteSheet(filename, c.KEY_SHEET_METADATA)
        self.currentFrame = 0
        self.image = self.spritesheet.get_image("press", self.currentFrame)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.lastUpdate = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.lastUpdate >= self.spritesheet.cooldown("press"):
            self.currentFrame += 1
            if self.currentFrame == self.spritesheet.num_frames("press"):
                self.currentFrame = 0
            self.image = self.spritesheet.get_image("press", self.currentFrame)
            self.lastUpdate = pygame.time.get_ticks()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

class NoteUi:
    def __init__(self):
        """Constructor.
        
            text: Text to display on note.
        """
        self.padding = 40
        self.backgroundRect = pygame.Rect()
        self.backgroundRect.width = c.SCREEN_WIDTH - 2 * self.padding
        self.backgroundRect.height = c.SCREEN_HEIGHT - 2 * self.padding
        self.backgroundRect.topleft = (self.padding, self.padding)

        self.innerTextMargin = 10
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)
        self.set_text("")

        self.isVisible = False

        # KeyUi Controls
        self.escapeKeyUi = KeyUi(pygame.K_ESCAPE, "Keys/Esc-Key.png", (0, 0))
        self.escapeKeyUi.rect.topright = (
            self.backgroundRect.topright[0] - 10,
            self.backgroundRect.topright[1]
        )

        self.xKeyUi = KeyUi(pygame.K_x, "Keys/X-Key.png", (0, 0))
        self.xKeyUi.rect.bottomleft = (
            self.backgroundRect.left + 10,
            self.backgroundRect.bottom - 10
        )
        self.xKeyHelpTextImage = self.font.render("Open Problem", True, 'white')
        self.xKeyHelpTextRect = self.xKeyHelpTextImage.get_rect()
        self.xKeyHelpTextRect.bottomleft = (
            self.xKeyUi.rect.right + 5,
            self.xKeyUi.rect.bottom
        )

        self.hKeyUi = KeyUi(pygame.K_h, "Keys/H-Key.png", (0, 0))
        self.hKeyUi.rect.bottomleft = (
            self.xKeyHelpTextRect.right + 10,
            self.backgroundRect.bottom - 10
        )
        self.hKeyHelpTextImage = self.font.render("Get Hint", True, 'white')
        self.hKeyHelpTextRect = self.hKeyHelpTextImage.get_rect()
        self.hKeyHelpTextRect.bottomleft = (
            self.hKeyUi.rect.right + 5,
            self.hKeyUi.rect.bottom
        )

        self.sKeyUi = KeyUi(pygame.K_s, "Keys/S-Key.png", (0, 0))
        self.sKeyUi.rect.bottomleft = (
            self.hKeyHelpTextRect.right + 10,
            self.backgroundRect.bottom - 10
        )
        self.sKeyHelpTextImage = self.font.render("Skip", True, 'white')
        self.sKeyHelpTextRect = self.sKeyHelpTextImage.get_rect()
        self.sKeyHelpTextRect.bottomleft = (
            self.sKeyUi.rect.right + 5,
            self.sKeyUi.rect.bottom
        )

        # Event subscribers
        EventManager.subscribe(EcodeEvent.OPEN_NOTE, self.set_text)
    
    def set_text(self, text: str, url: str=None):
        self.text = text
        self.url = url
        self.noteTextImage = self.font.render(self.text, True, 'white', wraplength=self.backgroundRect.width - 2 * self.innerTextMargin)
        self.noteTextRect = self.noteTextImage.get_rect()
        self.noteTextRect.topleft = (self.padding + self.innerTextMargin, self.padding + self.innerTextMargin)
        self.isVisible = True

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isVisible = False
                elif event.key == pygame.K_x:
                    EventManager.emit(EcodeEvent.OPEN_PROBLEM, url=self.url)

    def update(self):
        self.escapeKeyUi.update()
        self.xKeyUi.update()
        self.hKeyUi.update()
        self.sKeyUi.update()

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            surface.blit(self.noteTextImage, self.noteTextRect)
            self.escapeKeyUi.draw(surface)
            self.xKeyUi.draw(surface)
            surface.blit(self.xKeyHelpTextImage, self.xKeyHelpTextRect)
            self.hKeyUi.draw(surface)
            surface.blit(self.hKeyHelpTextImage, self.hKeyHelpTextRect)
            self.sKeyUi.draw(surface)
            surface.blit(self.sKeyHelpTextImage, self.sKeyHelpTextRect)

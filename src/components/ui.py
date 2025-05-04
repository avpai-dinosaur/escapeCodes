"""
ui.py
Individual ui components that live in screen space.
"""

import pygame
from bs4 import BeautifulSoup
from src.core.spritesheet import SpriteSheet
from src.core.ecodeEvents import EcodeEvent, EventManager
from src.core import utils
from src import constants as c
from src.components.button import TextInput


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
        pos: pygame.Vector2=pygame.Vector2(0, 0),
        caption="",
        font=utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)
    ):
        """Constructor.
        
            key: The key (e.g. pygame.K_m).
            filename: The key spritesheet.
            pos: Position of the ui element.
            caption: Text to display next to ui element.
            font: Font to render caption in.
        """
        self.key = key
        
        # Press key animation
        self.currentFrame = 0
        self.lastUpdate = pygame.time.get_ticks()
        self.spritesheet = SpriteSheet(filename, c.KEY_SHEET_METADATA)
        self.image = self.spritesheet.get_image("press", self.currentFrame)
        self.imageRect = self.image.get_rect()
        self.imageRect.topleft = (0, 0)

        # Caption
        self.font = font
        self.caption = caption
        self.captionMargin = 5
        self.captionImage = self.font.render(self.caption, True, 'white')
        self.captionRect = self.captionImage.get_rect()
        self.captionRect.bottomleft = (
            self.imageRect.right + self.captionMargin,
            self.imageRect.bottom
        )

        # Internal surface
        self.rect = pygame.Rect(
            pos.x, pos.y,
            self.imageRect.width + self.captionRect.width + self.captionMargin,
            max(self.imageRect.height, self.captionRect.height)
        )
        self.internalSurface = pygame.Surface(self.rect.size, pygame.SRCALPHA).convert_alpha()

    def update(self):
        if pygame.time.get_ticks() - self.lastUpdate >= self.spritesheet.cooldown("press"):
            self.currentFrame += 1
            if self.currentFrame == self.spritesheet.num_frames("press"):
                self.currentFrame = 0
            self.image = self.spritesheet.get_image("press", self.currentFrame)
            self.lastUpdate = pygame.time.get_ticks()

    def draw(self, surface: pygame.Surface):
        self.internalSurface.fill((0, 0, 0, 0))
        self.internalSurface.blit(self.image, self.imageRect)
        self.internalSurface.blit(self.captionImage, self.captionRect)
        surface.blit(self.internalSurface, self.rect)


class NoteUi:
    """Class representing ui for reading a note."""

    def __init__(self):
        """Constructor.
        
            text: Text to display on note.
        """
        self.noteMargin = 40
        self.backgroundRect = pygame.Rect()
        self.backgroundRect.width = c.SCREEN_WIDTH - 2 * self.noteMargin
        self.backgroundRect.height = c.SCREEN_HEIGHT - 2 * self.noteMargin
        self.backgroundRect.topleft = (self.noteMargin, self.noteMargin)

        self.keyControls = KeyControlBarUi()
        self.keyControls.add_control(KeyUi(pygame.K_o, "Keys/O-Key.png", caption="Open Problem"))
        self.keyControls.add_control(KeyUi(pygame.K_s, "Keys/S-Key.png", caption="Skip"))
        self.keyControls.add_control(KeyUi(pygame.K_ESCAPE, "Keys/Esc-Key.png", caption="Close Note"))
        self.keyControls.build()
        self.keyControls.rect.bottomleft = (
            self.backgroundRect.left + 10,
            self.backgroundRect.bottom - 10
        )

        self.textUiMargin = 10
        self.textUi = ScrollableTextUi(
            pygame.Vector2(
                self.backgroundRect.left + self.textUiMargin,
                self.backgroundRect.top + self.textUiMargin
            ),
            self.backgroundRect.width - 2 * self.textUiMargin,
            self.backgroundRect.height - self.keyControls.rect.height - 2 * self.textUiMargin
        )
        self.set_text("")

        self.isVisible = False
        self.isSolved = False

        # Solved Text
        self.solvedFont = utils.load_font("Monoton/Monoton-Regular.ttf", 50)
        self.solvedTextImage = self.solvedFont.render("Solved", True, 'green')
        self.solvedTextRect = self.solvedTextImage.get_rect()
        self.solvedTextRect.bottomright = (
            self.backgroundRect.right - 10,
            self.backgroundRect.bottom
        )

        # Event subscribers
        EventManager.subscribe(EcodeEvent.OPEN_NOTE, self.set_text)
    
    def set_text(self, text: str, url: str=None, isSolved: bool=False):
        self.textUi.set_text(text)
        self.url = url
        self.isSolved = isSolved
        self.isVisible = True

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            self.textUi.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isVisible = False
                elif event.key == pygame.K_x:
                    # TODO: probably don't want the LeetCodeManager to add the
                    # problem as an in progress problem if it was already
                    # solved
                    EventManager.emit(EcodeEvent.OPEN_PROBLEM, url=self.url)
                elif event.key == pygame.K_s:
                    EventManager.emit(
                        EcodeEvent.PROBLEM_SOLVED,
                        problemSlug=utils.get_problem_slug(self.url)
                    )

    def update(self):
        self.textUi.update()
        self.keyControls.update()

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            self.keyControls.draw(surface)
            self.textUi.draw(surface)
            if self.isSolved:
                surface.blit(self.solvedTextImage, self.solvedTextRect)


class TestCaseBattleUi:
    """Class representing ui for reading a note."""

    def __init__(self):
        """Constructor.
        
            text: Text to display on note.
        """
        self.noteMargin = 40
        self.backgroundRect = pygame.Rect()
        self.backgroundRect.width = c.SCREEN_WIDTH - 2 * self.noteMargin
        self.backgroundRect.height = c.SCREEN_HEIGHT - 2 * self.noteMargin
        self.backgroundRect.topleft = (self.noteMargin, self.noteMargin)

        self.keyControls = KeyControlBarUi()
        self.keyControls.add_control(KeyUi(pygame.K_o, "Keys/O-Key.png", caption="Open Problem"))
        self.keyControls.add_control(KeyUi(pygame.K_s, "Keys/S-Key.png", caption="Skip"))
        self.keyControls.add_control(KeyUi(pygame.K_ESCAPE, "Keys/Esc-Key.png", caption="Close Note"))
        self.keyControls.build()
        self.keyControls.rect.bottomleft = (
            self.backgroundRect.left + 10,
            self.backgroundRect.bottom - 10
        )

        self.textUiMargin = 10
        self.textUi = ScrollableTextUi(
            pygame.Vector2(
                self.backgroundRect.left + self.textUiMargin,
                self.backgroundRect.top + self.textUiMargin
            ),
            self.backgroundRect.width / 2 - 2 * self.textUiMargin,
            self.backgroundRect.height - self.keyControls.rect.height - 2 * self.textUiMargin
        )
        self.set_text("")

        self.textInput = TextInput((self.backgroundRect.left + (self.backgroundRect.width / 4) * 3, self.backgroundRect.top + self.backgroundRect.height / 2), 200, 45)

        self.isVisible = False
    
    def set_text(self, text: str):
        self.textUi.set_text(text)
        self.isVisible = True

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            self.textUi.handle_event(event)
            self.textInput.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isVisible = False
        elif event.type == c.PROBLEM_DESCRIPTION:
            self.set_text(BeautifulSoup(event.html, "html.parser").get_text())
    
    def update(self):
        self.textUi.update()
        self.keyControls.update()
        self.textInput.update(pygame.mouse.get_pos())

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            self.keyControls.draw(surface)
            self.textUi.draw(surface)
            self.textInput.draw(surface)





class KeyControlBarUi:
    """Class representing a control bar of KeyUis."""

    def __init__(self):
        """Constructor."""
        self.rect = pygame.Rect()
        self.controlMargin = 10
        self.controls: list[KeyUi] = []
    
    def add_control(self, keyUi: KeyUi):
        """Add a control to the control bar."""
        self.controls.append(keyUi)
    
    def build(self):
        """Build the bar with added controls.
        
            Must be called before draw().
        """
        self.width = self.controlMargin
        for ctrl in self.controls:
            ctrl.rect.left = self.width
            ctrl.rect.top = 0
            self.width += ctrl.rect.width + 10
        self.height = max(c.rect.height for c in self.controls)
        self.rect.size = (self.width, self.height)
        self.internalSurface = pygame.Surface(self.rect.size, pygame.SRCALPHA).convert_alpha()
    
    def update(self):
        [c.update() for c in self.controls]

    def draw(self, surface: pygame.Surface):
        self.internalSurface.fill((0, 0, 0, 0))
        [c.draw(self.internalSurface) for c in self.controls]
        surface.blit(self.internalSurface, self.rect)


class ScrollableTextUi:
    """Class representing scrollable text ui element."""

    def __init__(
        self, pos: pygame.Vector2, width: int, height: int,
        font=utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)    
    ):
        """Constructor.
        
            pos: Coordinates of left top corner of the element.
            width: Width of the element.
            height: Height of the element.
            font: Font to render text with.
        """
        self.rect = pygame.Rect(pos.x, pos.y, width, height)
        self.font = font
        self.scrollBarTrackWidth = 10
        self.internalSurface = pygame.Surface(self.rect.size, pygame.SRCALPHA).convert_alpha()
        self.set_text("")
    
    def set_text(self, textInput: str):
        self.text = textInput
        self.textImage = self.font.render(
            self.text, True, 'white',
            wraplength=self.rect.width - self.scrollBarTrackWidth
        )
        self.textRect = self.textImage.get_rect()
        self.textRect.topleft = (0, 0)

        # Create the scroll bar
        self.scrollBar = None
        self.showScrollBar = False
        if self.textRect.height > self.rect.height:
            self.scrollBar = pygame.Rect()
            self.scrollBar.width = self.scrollBarTrackWidth
            self.scrollBar.height = self.internalSurface.height ** 2 // self.textRect.height
            self.scrollBar.top = 0
            self.scrollBar.right = self.internalSurface.width
    
    def update(self):
        self.showScrollBar = utils.is_mouse_in_rect(self.rect)

    def handle_event(self, event: pygame.Event):
        if event.type == pygame.MOUSEWHEEL and utils.is_mouse_in_rect(self.rect):
            scroll = (
                (event.y < 0 and self.textRect.bottom > self.rect.height)
                or (event.y > 0 and self.textRect.top < 0)
            )
            if scroll:
                # Scale scroll distance by the height of one character
                distanceY = event.y * self.font.size("c")[1]
                self.textRect.top += distanceY
                self.scrollBar.top = -(self.textRect.top * self.internalSurface.height) // self.textRect.height

    def draw(self, surface: pygame.Surface):
        self.internalSurface.fill((0, 0, 0, 0))
        self.internalSurface.blit(self.textImage, self.textRect)
        if self.scrollBar is not None and self.showScrollBar:
            pygame.draw.rect(self.internalSurface, "grey", self.scrollBar)
        surface.blit(self.internalSurface, self.rect)


class MovingBarUi:
    """Class representing moving bar ui element."""

    def __init__(self):
        """Constructor."""
        self.width = 200
        self.height = 50
        self.centerx = c.SCREEN_WIDTH / 2
        self.yPos = c.SCREEN_HEIGHT - self.height - 50
        self.cursorWidth = 10
        self.cursorSpeed = 5
        self.rect = pygame.rect.Rect(0, self.yPos, self.width, self.height)
        self.rect.centerx = self.centerx
        self.innerRect = pygame.rect.Rect(0, self.yPos, self.width / 4, self.height)
        self.innerRect.centerx = self.rect.centerx
        self.cursor = pygame.rect.Rect(0, self.yPos, self.cursorWidth, self.height)
        self.cursor.left = self.rect.left
        self.leftCursorTarget = pygame.Vector2(self.rect.left + self.cursorWidth / 2, self.rect.top)
        self.rightCursorTarget = pygame.Vector2(self.rect.right - self.cursorWidth / 2, self.rect.top)
        self.isCursorMovingRight = False
        self.moveCursor = False
        self.keyUi = KeyUi(pygame.K_l, "Keys/L-Key.png", pygame.Vector2(self.rect.right + 10, self.rect.top - 10))

        # Event subscribers
        EventManager.subscribe(EcodeEvent.OPEN_BAR, self.on_open_bar)
    
    def on_open_bar(self):
        self.moveCursor = True

    def update(self):
        if self.moveCursor:
            if self.isCursorMovingRight:
                nextPos = utils.linear_move(pygame.Vector2(self.cursor.centerx, self.cursor.top), self.rightCursorTarget, self.cursorSpeed)
                if nextPos == self.rightCursorTarget:
                    self.isCursorMovingRight = False
            else:
                nextPos = utils.linear_move(pygame.Vector2(self.cursor.centerx, self.cursor.top), self.leftCursorTarget, self.cursorSpeed)
                if nextPos == self.leftCursorTarget:
                    self.isCursorMovingRight = True
            self.cursor.centerx = nextPos.x
            self.cursor.top = nextPos.y
            self.keyUi.update()
    
    def handle_event(self, event: pygame.Event):
        if self.moveCursor:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                self.moveCursor = False
                if self.cursor.colliderect(self.innerRect):
                    EventManager.emit(EcodeEvent.HIT_BAR)

    def draw(self, surface: pygame.Surface):
        if self.moveCursor:
            pygame.draw.rect(surface, "grey", self.rect)
            pygame.draw.rect(surface, "green", self.innerRect)
            pygame.draw.rect(surface, "red", self.cursor)
            self.keyUi.draw(surface)
        
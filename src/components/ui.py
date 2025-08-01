"""
ui.py
Individual ui components that live in screen space.
"""

import pygame
from bs4 import BeautifulSoup
from src.entities.problem import Parameter, Problem, ProblemFactory
from src.core.spritesheet import SpriteSheet
from src.core.ecodeEvents import EcodeEvent, EventManager
from src.core import utils
from src import constants as c
from src.components.button import TextInput
from src.components.scrollable import ScrollableTextUi
from src.core.fontManager import FontManager


class WasdUi:
    """Class representing 'WASD to move' ui instruction."""

    def __init__(self, on_close, pos: pygame.Vector2):
        """Constructor.
        
            pos: Position of the ui instruction.
        """
        self.on_close = on_close
        self.spritesheet = SpriteSheet("wasd.png", c.WASD_SHEET_METADATA)
        self.currentFrame = 0
        self.image = self.spritesheet.get_image("press", self.currentFrame)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.lastUpdate = pygame.time.get_ticks()
        self.isVisible = True

    def update(self):
        if pygame.time.get_ticks() - self.lastUpdate >= self.spritesheet.cooldown("press"):
            self.currentFrame += 1
            if self.currentFrame == self.spritesheet.num_frames("press"):
                self.currentFrame = 0
            self.image = self.spritesheet.get_image("press", self.currentFrame)
            self.lastUpdate = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                self.on_close(WasdUi)

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            surface.blit(self.image, self.rect)


class KeyPromptUi:
    """Class representing 'press key' prompt animation."""

    def __init__(
        self,
        key: int,
        filename: str,
        fileMetadata: dict=c.SM_KEY_SHEET_METADATA,
        pos: pygame.Vector2=pygame.Vector2(0, 0),
        caption="",
        font=None
    ):
        """Constructor.
        
            key: The key (e.g. pygame.K_m).
            filename: The key spritesheet.
            fileMetadata: The metadata for the key spritesheet.
            pos: Position of the ui element.
            caption: Text to display next to ui element.
            font: Font to render caption in.
        """
        self.key = key
        
        # Press key animation
        self.currentFrame = 0
        self.lastUpdate = pygame.time.get_ticks()
        self.spritesheet = SpriteSheet(filename, fileMetadata)
        self.image = self.spritesheet.get_image("press", self.currentFrame)
        self.imageRect = self.image.get_rect()
        self.imageRect.topleft = (0, 0)

        # Caption
        if font is None:
            self.font = FontManager.get_font("SpaceMono/SpaceMono-Regular.ttf", 20)
        else:
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

    def draw(self, surface: pygame.Surface, offset=pygame.Vector2(0, 0)):
        self.internalSurface.fill((0, 0, 0, 0))
        self.internalSurface.blit(self.image, self.imageRect)
        self.internalSurface.blit(self.captionImage, self.captionRect)
        surface.blit(self.internalSurface, self.rect.move(offset.x, offset.y))


class StandAloneKeyPromptUi(KeyPromptUi):
    """Class representing a stand alone key prompt ui element."""

    def __init__(
        self,
        on_close,
        key: int,
        filename: str,
        fileMetadata: dict=c.SM_KEY_SHEET_METADATA,
        pos: pygame.Vector2=pygame.Vector2(0, 0),
        caption: str=""
    ):
        """Constructor."""
        super().__init__(key, filename, fileMetadata, pos, caption)
        self.on_close = on_close
    
    def handle_event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.key:
                self.on_close(StandAloneKeyPromptUi)


class ParameterInputUi:
    """Class representing ui component for inputing multiple parameters."""

    def __init__(self, width, pos: pygame.Vector2):
        """Constructor."""
        self.pos = pos
        self.width = width
        self.height = 0
        self.parameters: list[Parameter] = []
        self.fieldMargin = 10
        self.fieldCaptionFont = utils.load_font("SpaceMono/SpaceMono-Italic.ttf")
    
    def add_parameter(self, parameter: Parameter) -> None:
        self.parameters.append(parameter)
    
    def build(self) -> None:
        """Build the ui element with all added parameters.
        
            Must be called before draw
        """
        # Generate all caption images, caption rects, and text input boxes
        self.fieldCaptionImages : list[pygame.Surface] = [
            self.fieldCaptionFont.render(f"{param.name}=", True, "white")
            for param in self.parameters
        ]
        self.fieldCaptionRects = [
            caption.get_rect()
            for caption in self.fieldCaptionImages
        ]
        self.fieldInputs = [
            TextInput((0, 0), self.width, 45)
            for _ in self.fieldCaptionRects
        ]

        # Position each parameter element
        for field in zip(self.fieldCaptionRects, self.fieldInputs):
            self.height += self.fieldMargin
            field[0].top = self.pos.y + self.height
            field[0].left = self.pos.x
            self.height += field[0].height
            field[1].rect.top = self.pos.y + self.height
            field[1].rect.left = self.pos.x
            self.height += field[1].rect.height

    def get_inputs(self):
        inputs = {}
        for i in range(len(self.parameters)):
            inputs[self.parameters[i].name] = self.parameters[i].parse(self.fieldInputs[i].textBuffer)
        return inputs

    def handle_event(self, event: pygame.Event):
        for fieldInput in self.fieldInputs:
            fieldInput.handle_event(event)

    def update(self):
        for fieldInput in self.fieldInputs:
            fieldInput.update(pygame.mouse.get_pos())

    def draw(self, surface: pygame.Surface):
        for field in zip(self.fieldCaptionImages, self.fieldCaptionRects):
           surface.blit(field[0], field[1])
        for fieldInput in self.fieldInputs:
            fieldInput.draw(surface)


class KeyPromptControlBarUi:
    """Class representing a control bar of KeyPromptUis."""

    def __init__(self):
        """Constructor."""
        self.rect = pygame.Rect()
        self.controlMargin = 10
        self.controls: list[KeyPromptUi] = []
    
    def add_control(self, keyUi: KeyPromptUi):
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
        self.keyUi = KeyPromptUi(pygame.K_l, "Keys/L-Key.png", pos=pygame.Vector2(self.rect.right + 10, self.rect.top - 10))

        # Event subscribers
        EventManager.subscribe(EcodeEvent.BOSS_CHARGE, self.open)
        EventManager.subscribe(EcodeEvent.BOSS_ATTACK, self.close)
    
    def open(self):
        self.moveCursor = True

    def close(self):
        self.moveCursor = False

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


class DialogUi:
    """Class representing a dialog ui element."""

    def __init__(self, on_close, lines, currentLine):
        """Constructor."""
        self.rect = pygame.Rect()
        self.rect.width = c.SCREEN_WIDTH
        self.rect.height = (c.SCREEN_HEIGHT) / 4
        self.rect.bottom = c.SCREEN_HEIGHT
        self.textLeft = self.rect.width // 5

        self.keyPromptUi = KeyPromptUi(pygame.K_SPACE, "Keys/Space-Key.png", c.LG_KEY_SHEET_METADATA)
        self.keyPromptUi.rect.bottom = self.rect.bottom - 10
        self.keyPromptUi.rect.right = self.rect.right - 10

        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", size=20)

        self.on_close = on_close
        self.lines = lines
        self.currentLine = currentLine
        self.set_dialog(self.lines[self.currentLine])
        
    def set_dialog(self, text: str):
        """Set the dialog text."""
        self.textImage = self.font.render(text, True, "white", wraplength=self.rect.right - self.textLeft)
        self.textRect = self.textImage.get_rect()
        self.textRect.top = self.rect.top + 10
        self.textRect.left = self.textLeft

    def next_line(self):
        """Proceed to next line of dialog."""
        self.currentLine += 1
        if self.currentLine >= len(self.lines):
            EventManager.emit(EcodeEvent.UNPAUSE_GAME)
            EventManager.emit(EcodeEvent.FINISHED_DIALOG)
            self.on_close(DialogUi)
        else:
            self.set_dialog(self.lines[self.currentLine])
    
    def handle_event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.next_line()
    
    def update(self):
        self.keyPromptUi.update()
                    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, "blue", self.rect)
        surface.blit(self.textImage, self.textRect)
        self.keyPromptUi.draw(surface)

class PinPad:
    """Class to represent a pin pad."""

    class KeyUi:
        """Class representing a key ui element."""

        def __init__(
            self,
            key: int,
            filename: str,
            size: str="small"
        ):
            self.key = key
            self.pressed = False
            metadata = (
                c.SM_KEY_SHEET_METADATA if size == "small"
                    else c.MD_KEY_SHEET_METADATA if size == "medium"
                        else c.LG_KEY_SHEET_METADATA
            )
            self.spritesheet = SpriteSheet(filename, metadata)
            self.notPressedImage = self.spritesheet.get_image("press", 0)
            self.pressedImage = self.spritesheet.get_image("press", 1)
            self.imageRect = self.pressedImage.get_rect()
    
        def update(self, pressedKeys):
            self.pressed = pressedKeys[self.key]

        def draw(self, surface: pygame.Surface):
            surface.blit(
                self.pressedImage if self.pressed else self.notPressedImage,
                self.imageRect
            )

    def __init__(self):
        # Input Screen
        self.pin = None
        self.inputBuffer = ["0", "0", "0", "0"]
        self.inputPtr = 0
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 60)
        self.render_input_screen()

        # Key grid
        self.keys = [
            [
                PinPad.KeyUi(pygame.K_1, "Keys/1-Key.png"),
                PinPad.KeyUi(pygame.K_2, "Keys/2-Key.png"),
                PinPad.KeyUi(pygame.K_3, "Keys/3-Key.png")
            ],
            [
                PinPad.KeyUi(pygame.K_4, "Keys/4-Key.png"),
                PinPad.KeyUi(pygame.K_5, "Keys/5-Key.png"),
                PinPad.KeyUi(pygame.K_6, "Keys/6-Key.png")
            ],
            [
                PinPad.KeyUi(pygame.K_7, "Keys/7-Key.png"),
                PinPad.KeyUi(pygame.K_8, "Keys/8-Key.png"),
                PinPad.KeyUi(pygame.K_9, "Keys/9-Key.png")
            ],
            [
                PinPad.KeyUi(pygame.K_BACKSPACE, "Keys/Del-Key.png"),
                PinPad.KeyUi(pygame.K_0, "Keys/0-Key.png"),
                PinPad.KeyUi(pygame.K_RETURN, "Keys/ArrowRet-Key.png")
            ]
        ]

        keyHeight = self.keys[0][0].imageRect.height
        keyWidth = self.keys[0][0].imageRect.width
        self.keyGridRect = pygame.Rect(0, 0, len(self.keys[0]) * keyWidth, len(self.keys) * keyHeight)
        self.keyGridInternalSurface = pygame.Surface(self.keyGridRect.size, pygame.SRCALPHA).convert_alpha()

        for i in range(len(self.keys)):
            for j in range(len(self.keys[i])):
                pos = pygame.Vector2(j * keyWidth, i * keyHeight)
                self.keys[i][j].imageRect.topleft = pos
        
        # Background
        self.backgroundRect = pygame.Rect(0, 0, self.keyGridRect.width + 20, self.keyGridRect.height + self.inputScreenRect.height + 20)
        self.backgroundRect.centerx = c.SCREEN_WIDTH // 2
        self.backgroundRect.centery = c.SCREEN_HEIGHT // 2
        self.inputScreenRect.centerx = self.backgroundRect.centerx
        self.inputScreenRect.top = self.backgroundRect.top + 10
        self.keyGridRect.centerx = self.inputScreenRect.centerx
        self.keyGridRect.top = self.inputScreenRect.bottom

        self.isVisible = False

        # Event subscribers
        EventManager.subscribe(EcodeEvent.OPEN_PIN, self.open)

        #ESC
        self.ESC = KeyPromptControlBarUi()
        self.ESC.controls.clear()
        self.ESC.add_control(KeyPromptUi(pygame.K_q, "Keys/Esc-Key.png", caption=" to exit"))
        self.ESC.build()
        self.ESC.rect.center = (
            self.backgroundRect.centerx, self.keyGridRect.bottom + 50
        )


    def render_input_screen(self):
        self.inputDigitImages = [self.font.render(digit, True, "white") for digit in self.inputBuffer]
        self.inputDigitRects = [image.get_rect() for image in self.inputDigitImages]
        digitWidth, digitHeight = self.inputDigitRects[0].size
        digitMargin = 5
        self.inputScreenRect = pygame.Rect(0, 0, digitMargin + (digitWidth + digitMargin) * len(self.inputBuffer), digitHeight)
        self.inputScreenInternalSurface = pygame.Surface(self.inputScreenRect.size, pygame.SRCALPHA).convert_alpha()
        for i in range(len(self.inputDigitRects)):
            self.inputDigitRects[i].left = digitMargin + i * (digitWidth + digitMargin)

    def open(self, pin: int, id: int):
        self.inputBuffer = ["0", "0", "0", "0"]
        self.inputPtr = 0
        self.isVisible = True
        self.pin = pin
        self.doorId = id
        EventManager.emit(EcodeEvent.PAUSE_GAME)

    def update(self):
        pressedKeys = pygame.key.get_pressed()
        for keyRow in self.keys:
            for key in keyRow:
                key.update(pressedKeys)    
        self.ESC.update()

    def handle_event(self, event: pygame.Event):
        if self.isVisible: 
            if event.type == pygame.KEYDOWN:
                if event.unicode.isdigit():
                    self.inputBuffer[self.inputPtr] = event.unicode
                    self.inputPtr = min(len(self.inputBuffer) - 1, self.inputPtr + 1)
                elif event.key == pygame.K_BACKSPACE:
                    self.inputBuffer[self.inputPtr] = "0"
                    self.inputPtr = max(0, self.inputPtr - 1)
                elif event.key == pygame.K_RETURN:
                    input = ""
                    for digit in self.inputBuffer:
                        input += digit
                    input = int(input)
                    if input == self.pin:
                        self.isVisible = False
                        EventManager.emit(EcodeEvent.OPEN_DOOR, id=self.doorId)
                        EventManager.emit(EcodeEvent.UNPAUSE_GAME)
                elif event.key == pygame.K_ESCAPE:
                    self.isVisible = False
                    EventManager.emit(EcodeEvent.UNPAUSE_GAME)
                
    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, "blue", self.backgroundRect, border_radius=10)

            self.inputScreenInternalSurface.fill((0, 0, 0, 0))
            for i in range(len(self.inputBuffer)):
                color = "red" if i == self.inputPtr else "white"
                self.inputDigitImages[i] = self.font.render(self.inputBuffer[i], True, color)
                self.inputScreenInternalSurface.blit(self.inputDigitImages[i], self.inputDigitRects[i])
            surface.blit(self.inputScreenInternalSurface, self.inputScreenRect)

            self.keyGridInternalSurface.fill((0, 0, 0, 0))
            for keyRow in self.keys:
                for key in keyRow:
                    key.draw(self.keyGridInternalSurface)
            surface.blit(self.keyGridInternalSurface, self.keyGridRect)
            self.ESC.draw(surface)
            
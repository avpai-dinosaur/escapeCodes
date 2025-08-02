import pygame
import src.constants as c
import src.core.utils as utils
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.components.ui import KeyPromptControlBarUi, KeyPromptUi, ScrollableTextUi
from src.components.button import TextInput


class DownloadUi:
    """Class representing ui for reading a note."""

    def __init__(self, on_close):
        """Constructor.

            on_close: Callback function provided by UiManager
        """
        self.noteMargin = 40
        self.backgroundRect = pygame.Rect()
        self.backgroundRect.width = c.SCREEN_WIDTH - 2 * self.noteMargin
        self.backgroundRect.height = c.SCREEN_HEIGHT - 2 * self.noteMargin
        self.backgroundRect.topleft = (self.noteMargin, self.noteMargin)

        self.keyControls = KeyPromptControlBarUi()
        self.keyControls.add_control(KeyPromptUi(pygame.K_ESCAPE, "Keys/Esc-Key.png", caption="Close Note"))
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
            self.backgroundRect.height - self.keyControls.rect.height - 2 * self.textUiMargin,
            utils.load_font("SpaceMono/SpaceMono-Regular.ttf")
        )
        self.solvedFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 50)
        self.set_text("")

        # Probe word text input 
        self.probePromptFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)
        self.probePromptImage = self.probePromptFont.render("Enter word index to probe:", True, "white")
        self.probePromptRect = self.probePromptImage.get_rect()
        self.probeUi = TextInput(
            pos=(0, 0),
            width=100,
            height=40,
            font=utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30),
            onSubmit=self.on_probe_submit
        )
        self.probeUi.rect.bottomright = ( 
            self.backgroundRect.right - 10,
            self.backgroundRect.bottom - 10
        )
        self.probePromptRect.bottom = self.probeUi.rect.bottom
        self.probePromptRect.right = self.probeUi.rect.left - 10
        self.probeUiActive = False

        self.solvedTextImage = None
        self.solvedTextRect = None

        self.isVisible = False
        self.isSolved = False
        self.on_close = on_close
    
    def set_text(self, text: str, isProbeActive: bool=False):
        self.textUi.set_text(text)
        self.probeUiActive = isProbeActive
        self.isVisible = True
        EventManager.emit(EcodeEvent.PAUSE_GAME)
 
    def on_probe_submit(self, textInput):
        try:
            wordIdx = int(textInput)
            EventManager.emit(EcodeEvent.TRY_PROBE, wordIdx=wordIdx)
        except ValueError:
            pass

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            self.textUi.handle_event(event)
            self.probeUi.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isVisible = False
                    EventManager.emit(EcodeEvent.UNPAUSE_GAME)
                    self.on_close(DownloadUi)

    def update(self):
        self.textUi.update()
        self.probeUi.update(pygame.mouse.get_pos())
        self.keyControls.update()

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            self.keyControls.draw(surface)
            self.textUi.draw(surface)
            surface.blit(self.probePromptImage, self.probePromptRect)
            self.probeUi.draw(surface)
            

if __name__ == "__main__":
    from src.core.leetcodeManager import LeetcodeManager
    from src.entities.computer import SnippableComputer

    pygame.init()
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("Scrollable")
    clock = pygame.time.Clock()

    leetcodeManager = LeetcodeManager()
    leetcodeManager.username = "escapeCodesTest"
    computer = SnippableComputer(
        pygame.Rect(400, 400, 1, 1),
        "hello\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nthis is a note",
    )
    mockPlayer = type('MockPlayer', (object,), {'rect': pygame.Rect(400, 400, 1, 1)})()
    downloadUi = DownloadUi(lambda x: None)
    EventManager.subscribe(EcodeEvent.OPEN_DOWNLOAD, downloadUi.set_text)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            computer.handle_event(event)
            downloadUi.handle_event(event)

        computer.update(mockPlayer)
        downloadUi.update()
        
        screen.fill("black")
        computer.draw(screen, pygame.Vector2(0, 0))
        downloadUi.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
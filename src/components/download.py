import pygame
import src.constants as c
import src.core.utils as utils
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.components.ui import KeyPromptControlBarUi, KeyPromptUi, ScrollableTextUi
from src.components.button import TextInput


class DownloadUi:
    """Class representing ui for a note with downloadable snippets."""

    PhraseStartWord = "STARTPHRASE"
    PhraseEndWord = "ENDPHRASE"

    def __init__(self, on_close):
        """Constructor.

            on_close: Callback function provided by UiManager
            computer: Reference to computer this ui belongs to
        """
        self.noteMargin = 40
        self.backgroundRect = pygame.Rect()
        self.backgroundRect.width = c.SCREEN_WIDTH - 2 * self.noteMargin
        self.backgroundRect.height = c.SCREEN_HEIGHT - 2 * self.noteMargin
        self.backgroundRect.topleft = (self.noteMargin, self.noteMargin)

        self.keyControls = KeyPromptControlBarUi()
        self.keyControls.add_control(KeyPromptUi(pygame.K_ESCAPE, "Keys/Esc-Key.png", caption="Close Note"))
        self.keyControls.add_control(KeyPromptUi(pygame.K_t, "Keys/T-Key.png", caption="Toggle View"))
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
            self.backgroundRect.height - self.keyControls.rect.height - 2 * self.textUiMargin,
            utils.load_font("SpaceMono/SpaceMono-Regular.ttf")
        )
        self.solvedFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 50)

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

        # Parsing Errors
        self.errorTextFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", size=30)
        self.set_error_text("")

        # Success Message
        self.successTextFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", size=30)
        self.set_success_text("")

        # Headings
        self.headingMargin = 10
        self.headingFont = utils.load_font("SpaceMono/SpaceMono-Bold.ttf", 30)

        self.foundPhrasesHeadingImage = self.headingFont.render("Found Phrases", True, "white")
        self.foundPhrasesHeadingRect = self.foundPhrasesHeadingImage.get_rect()
        self.foundPhrasesHeadingRect.top = self.backgroundRect.top + self.headingMargin
        self.foundPhrasesHeadingRect.left = self.backgroundRect.left + self.backgroundRect.width / 2 + self.headingMargin

        # Found Phrases List
        self.foundPhrasesTextUi = ScrollableTextUi(
            pygame.Vector2(
                self.textUi.scrollableContainer.rect.right + self.textUiMargin,
                self.foundPhrasesHeadingRect.bottom + self.textUiMargin
            ),
            self.backgroundRect.width / 2 - 2 * self.textUiMargin,
            self.backgroundRect.height - self.keyControls.rect.height - self.foundPhrasesHeadingRect.height - 2 * self.textUiMargin,
            utils.load_font("SpaceMono/SpaceMono-Regular.ttf"),
            "green"
        )

        self.showIndices = False
        self.isVisible = False
        self.isSolved = False
        self.on_close = on_close
    
    def set_text(self, text: str, computer, isProbeActive: bool=True):
        self.computer = computer
        self.probeUiActive = isProbeActive
        self.set_textui_text()
        self.set_found_phrases()
        self.isVisible = True
        EventManager.emit(EcodeEvent.PAUSE_GAME)
    
    def set_textui_text(self):
        self.textUi.set_text(
            self.computer.get_text() if not self.showIndices else self.computer.get_text_with_indices()
        )

    def set_found_phrases(self):
        self.foundPhrasesTextUi.set_text(
            "\n".join([f"'{p}'" for p in self.computer.foundPhrases]) +
            f"\nHidden Phrases Left: {self.computer.get_num_phrases_left()}"
        )

    def set_error_text(self, text: str):
        self.errorTextImage = self.errorTextFont.render(text, True, "red")
        self.errorTextRect = self.errorTextImage.get_rect()
        self.errorTextRect.bottomright = self.probeUi.rect.topright
    
    def set_success_text(self, text: str):
        self.successTextImage = self.successTextFont.render(text, True, "green")
        self.successTextRect = self.successTextImage.get_rect()
        self.successTextRect.bottomright = self.probeUi.rect.topright

    def on_probe_submit(self, textInput):
        self.set_error_text("")
        self.set_success_text("")
        try:
            wordIdx = int(textInput)
        except ValueError:
            self.set_error_text(f"'{textInput}' is not a valid index")
            return
        phrase = self.computer.try_probe(wordIdx)
        if phrase is not None:
            self.set_success_text(f"Found phrase")
            self.set_found_phrases()
        else:
            if wordIdx < len(self.computer.words) or wordIdx < 0:
                self.set_error_text(f"'{self.computer.words[wordIdx]}' is not part of a phrase")
            else:
                self.set_error_text(f"Index {wordIdx} is out of bounds")

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            self.textUi.handle_event(event)
            self.foundPhrasesTextUi.handle_event(event)
            self.probeUi.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isVisible = False
                    EventManager.emit(EcodeEvent.UNPAUSE_GAME)
                    self.on_close(DownloadUi)
                if event.key == pygame.K_t:
                    self.showIndices = not self.showIndices
                    self.set_textui_text()

    def update(self):
        self.textUi.update()
        self.foundPhrasesTextUi.update()
        self.probeUi.update(pygame.mouse.get_pos())
        self.keyControls.update()

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            self.keyControls.draw(surface)
            self.textUi.draw(surface)
            self.foundPhrasesTextUi.draw(surface)
            surface.blit(self.errorTextImage, self.errorTextRect)
            surface.blit(self.successTextImage, self.successTextRect)
            surface.blit(self.foundPhrasesHeadingImage, self.foundPhrasesHeadingRect)
            if self.probeUiActive:
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
        "hello bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nthis is a note",
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
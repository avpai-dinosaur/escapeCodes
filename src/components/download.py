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

        # Parsing Errors
        self.errorTextFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", size=30)
        self.set_error_text("")

        # Success Message
        self.successTextFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", size=30)
        self.set_success_text("")

        self.solvedTextImage = None
        self.solvedTextRect = None

        self.isVisible = False
        self.isSolved = False
        self.on_close = on_close
    
    def set_text(self, text: str, isProbeActive: bool=True):
        self.probeUiActive = isProbeActive
        self.parse_text(text)
        self.textUi.set_text(
            self.get_text_with_indices() if self.probeUiActive else self.get_text()
        )
        self.isVisible = True
        EventManager.emit(EcodeEvent.PAUSE_GAME)

    def set_error_text(self, text: str):
        self.errorTextImage = self.errorTextFont.render(text, True, "red")
        self.errorTextRect = self.errorTextImage.get_rect()
        self.errorTextRect.bottomright = self.probeUi.rect.topright
    
    def set_success_text(self, text: str):
        self.successTextImage = self.successTextFont.render(text, True, "green")
        self.successTextRect = self.successTextImage.get_rect()
        self.successTextRect.bottomright = self.probeUi.rect.topright

    def parse_text(self, text: str):
        self.phrases = []
        self.lines = []
        self.words = []
        wordIdx = 0
        currentPhrase = None
        for line in text.split("\n"):
            self.lines.append([])
            for word in line.split(" "):
                if word == DownloadUi.PhraseStartWord:
                    if currentPhrase is not None:
                        raise ValueError("Attempted to start new phrase before closing current one")
                    currentPhrase = [wordIdx]
                elif word == DownloadUi.PhraseEndWord:
                    if currentPhrase is None:
                        raise ValueError("Attempted to close phrase before starting one")
                    currentPhrase.append(wordIdx)
                    self.phrases.append(currentPhrase.copy())
                    currentPhrase = None
                else:
                    self.lines[-1].append(word)
                    self.words.append(word)
                    wordIdx += 1

    def get_text(self):
        return "\n".join([" ".join(line) for line in self.lines])
    
    def get_text_with_indices(self):
        idx = 0
        modifiedLines = []
        for line in self.lines:
            modifiedLine = []
            for word in line:
                modifiedLine.append(f"{word}({idx})")
                idx += 1
            modifiedLines.append(" ".join(modifiedLine))
        return "\n".join(modifiedLines)

    def get_phrase(self, wordIdx):
        for phrase in self.phrases:
            if phrase[0] <= wordIdx < phrase[1]:
                return phrase
        return None

    def try_probe(self, wordIdx):
        phrase = self.get_phrase(wordIdx)
        if phrase is not None:
            joinedPhrase = " ".join(self.words[phrase[0]:phrase[1]])
            self.set_success_text(f"Found phrase '{joinedPhrase}'")
            EventManager.emit(EcodeEvent.SAVE_PHRASE, phrase=joinedPhrase)
        else:
            if wordIdx < len(self.words) or wordIdx < 0:
                self.set_error_text(f"'{self.words[wordIdx]}' is not part of a phrase")
            else:
                self.set_error_text(f"Index {wordIdx} is out of bounds")
    
    def on_probe_submit(self, textInput):
        self.set_error_text("")
        self.set_success_text("")
        try:
            wordIdx = int(textInput)
            self.try_probe(wordIdx)
        except ValueError:
            self.set_error_text(f"'{textInput}' is not a valid index")

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
            surface.blit(self.errorTextImage, self.errorTextRect)
            surface.blit(self.successTextImage, self.successTextRect)
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
import pygame
import src.constants as c
import src.core.utils as utils
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.components.ui import KeyPromptControlBarUi, KeyPromptUi, ScrollableTextUi


class NoteUi:
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

        self.solvedTextImage = None
        self.solvedTextRect = None

        self.isVisible = False
        self.isSolved = False
        self.on_close = on_close
    
    def set_text(self, text: str, url: str=None, isSolved: bool=False, pinText: str=""):
        self.textUi.set_text(text)

        self.url = url
        if self.url:
            self.solvedTextImage = (
                self.solvedFont.render(f"{pinText}", True, 'green') if isSolved
                else self.solvedFont.render("Unsolved", True, "red")
            )
            self.solvedTextRect = self.solvedTextImage.get_rect()
            self.solvedTextRect.bottomright = (
                self.backgroundRect.right - 10,
                self.backgroundRect.bottom
            )
            self.isSolved = isSolved

            self.keyControls.controls.clear()
            self.keyControls.add_control(KeyPromptUi(pygame.K_ESCAPE, "Keys/Esc-Key.png", caption="Close Note"))
            self.keyControls.add_control(KeyPromptUi(pygame.K_o, "Keys/O-Key.png", caption="Open Problem"))
            self.keyControls.add_control(KeyPromptUi(pygame.K_s, "Keys/S-Key.png", caption="Skip"))
            self.keyControls.add_control(KeyPromptUi(pygame.K_r, "Keys/R-Key.png", caption="Refresh"))
            self.keyControls.build()
        
        self.keyControls.rect.bottomleft = (
            self.backgroundRect.left + 10,
            self.backgroundRect.bottom - 10
        )

        self.isVisible = True

        EventManager.emit(EcodeEvent.PAUSE_GAME)

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            self.textUi.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isVisible = False
                    EventManager.emit(EcodeEvent.UNPAUSE_GAME)
                    self.on_close(self)
                elif self.url and event.key == pygame.K_o:
                    # TODO: probably don't want the LeetCodeManager to add the
                    # problem as an in progress problem if it was already
                    # solved
                    EventManager.emit(EcodeEvent.OPEN_PROBLEM, url=self.url)
                elif self.url and event.key == pygame.K_s:
                    EventManager.emit(
                        EcodeEvent.PROBLEM_SOLVED,
                        problemSlug=utils.get_problem_slug(self.url)
                    )
                elif self.url and event.key == pygame.K_r:
                    EventManager.emit(EcodeEvent.CHECK_PROBLEMS)

    def update(self):
        self.textUi.update()
        self.keyControls.update()

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            self.keyControls.draw(surface)
            self.textUi.draw(surface)
            if self.solvedTextImage and self.solvedTextRect:
                surface.blit(self.solvedTextImage, self.solvedTextRect)


if __name__ == "__main__":
    from src.core.leetcodeManager import LeetcodeManager
    from src.entities.objects import ProblemComputer

    pygame.init()
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("Scrollable")
    clock = pygame.time.Clock()

    leetcodeManager = LeetcodeManager()
    leetcodeManager.username = "escapeCodesTest"
    problemComputer = ProblemComputer(
        pygame.Rect(400, 400, 1, 1),
        "hello\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nthis is a note",
        "https://leetcode.com/problems/two-sum/description/",
        "_2_4"
    )
    mockPlayer = type('MockPlayer', (object,), {'rect': pygame.Rect(400, 400, 1, 1)})()
    noteUi = NoteUi(lambda x: None)
    EventManager.subscribe(EcodeEvent.OPEN_NOTE, noteUi.set_text)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            problemComputer.handle_event(event)
            noteUi.handle_event(event)

        problemComputer.update(mockPlayer)
        noteUi.update()
        
        screen.fill("black")
        problemComputer.draw(screen, pygame.Vector2(0, 0))
        noteUi.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
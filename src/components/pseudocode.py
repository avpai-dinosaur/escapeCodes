import pygame
from bs4 import BeautifulSoup
import src.components.ui as ui
import src.core.utils as utils
import src.constants as c
from src.core.ecodeEvents import EcodeEvent, EventManager


class PseudocodeUi:
    """Class representing ui for pseudocode puzzle."""

    showTutorial = True

    def __init__(self, on_close):
        """Constructor."""
        # Background
        self.margin = 40
        self.backgroundRect = pygame.Rect()
        self.backgroundRect.width = c.SCREEN_WIDTH - 2 * self.margin
        self.backgroundRect.height = c.SCREEN_HEIGHT - 2 * self.margin
        self.backgroundRect.topleft = (self.margin, self.margin)

        # Key Controls
        self.keyControls = ui.KeyPromptControlBarUi()
        self.keyControls.add_control(ui.KeyPromptUi(pygame.K_ESCAPE, "Keys/Esc-Key.png", caption="Close"))
        self.keyControls.build()
        self.keyControls.rect.bottomleft = (
            self.backgroundRect.left + 10,
            self.backgroundRect.bottom - 10
        )

        # Headings
        self.headingMargin = 10
        self.headingFont = utils.load_font("SpaceMono/SpaceMono-Bold.ttf", 30)

        self.leftTextImage = self.headingFont.render("Problem Description", True, "white")
        self.leftTextRect = self.leftTextImage.get_rect()
        self.leftTextRect.top = self.backgroundRect.top + self.headingMargin
        self.leftTextRect.left = self.backgroundRect.left + self.headingMargin

        self.rightTextImage = self.headingFont.render("Pseudocode", True, "white")
        self.rightTextRect = self.rightTextImage.get_rect()
        self.rightTextRect.top = self.backgroundRect.top + self.headingMargin
        self.rightTextRect.left = self.backgroundRect.left + self.backgroundRect.width / 2 + self.headingMargin

        # Problem Description
        self.problemUiMargin = 10
        self.problemUi = ui.ScrollableTextUi(
            pygame.Vector2(
                self.backgroundRect.left + self.problemUiMargin,
                self.leftTextRect.bottom + self.problemUiMargin
            ),
            self.backgroundRect.width / 2 - 2 * self.problemUiMargin,
            self.backgroundRect.height - self.keyControls.rect.height - self.leftTextRect.height - 2 * self.problemUiMargin,
            utils.load_font("SpaceMono/SpaceMono-Regular.ttf")
        )

        # Pseudocode
        self.pseudocodeUi = ui.ScrollableTextUi(
            pygame.Vector2(
                self.problemUi.scrollableContainer.rect.right + self.problemUiMargin,
                self.problemUi.scrollableContainer.rect.top
            ),
            self.backgroundRect.width / 2 - 2 * self.problemUiMargin,
            self.backgroundRect.height - self.keyControls.rect.height - self.leftTextRect.height - 2 * self.problemUiMargin,
            utils.load_font("SpaceMono/SpaceMono-Regular.ttf")
        )

        self.isVisible = False
        self.on_close = on_close

        if PseudocodeUi.showTutorial:
            EventManager.emit(
                EcodeEvent.GIVE_ORDER,
                text=
"""Explore the other terminals in the room to find snippets
which complete the pseudocode solution for the given problem."""
            )
            PseudocodeUi.showTutorial = False

    def set_text(self, text: str, problemSlug: str):
        self.pseudocodeUi.set_text(text)
        EventManager.emit(EcodeEvent.GET_PROBLEM_DESCRIPTION, problemSlug=problemSlug)
        EventManager.emit(EcodeEvent.PAUSE_GAME)

    def set_problem_description(self, text: str):
        self.problemUi.set_text(text)
        self.isVisible = True

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            self.problemUi.handle_event(event)
            self.pseudocodeUi.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.isVisible = False
                    self.on_close(PseudocodeUi)
                    EventManager.emit(EcodeEvent.UNPAUSE_GAME)
        elif event.type == c.PROBLEM_DESCRIPTION:
            self.set_problem_description(BeautifulSoup(event.html, "html.parser").get_text())
    
    def update(self):
        if self.isVisible:
            self.problemUi.update()
            self.pseudocodeUi.update()
            self.keyControls.update()

    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            self.keyControls.draw(surface)
            self.problemUi.draw(surface)
            self.pseudocodeUi.draw(surface)
            surface.blit(self.leftTextImage, self.leftTextRect)
            surface.blit(self.rightTextImage, self.rightTextRect)


if __name__ == "__main__":
    from src.core.leetcodeManager import LeetcodeManager
    from src.entities.computer import PseudocodeComputer 

    pygame.init()
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("Pseudocode")
    clock = pygame.time.Clock()

    leetcodeManager = LeetcodeManager()
    leetcodeManager.username = "escapeCodesTest"
    text = (
f"""L1
{PseudocodeComputer.HiddenLineWord} L2
    L3"""
    ) + "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nhello"
    pseudocodeComputer = PseudocodeComputer(pygame.Rect(400, 400, 1, 1), text)
    mockPlayer = type('MockPlayer', (object,), {'rect': pygame.Rect(400, 400, 1, 1)})()
    pseudocodeUi = PseudocodeUi(lambda x: None)
    EventManager.subscribe(EcodeEvent.OPEN_PSEUDOCODE, pseudocodeUi.set_text)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            pseudocodeComputer.handle_event(event)
            pseudocodeUi.handle_event(event)

        pseudocodeComputer.update(mockPlayer)
        pseudocodeUi.update()
        
        screen.fill("black")
        pseudocodeComputer.draw(screen, pygame.Vector2(0, 0))
        pseudocodeUi.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
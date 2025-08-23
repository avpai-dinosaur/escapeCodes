import pygame
from bs4 import BeautifulSoup
import src.components.ui as ui
import src.core.utils as utils
import src.constants as c
from src.core.ecodeEvents import EcodeEvent, EventManager
from src.entities.problem import Problem, ProblemFactory


class TestCaseHackUi:
    """Class representing ui for test case hack."""

    showTutorial = True

    def __init__(self, on_close, problemSlug: str):
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

        self.leftTextImage = self.headingFont.render("Intercepted Signal", True, "white")
        self.leftTextRect = self.leftTextImage.get_rect()
        self.leftTextRect.top = self.backgroundRect.top + self.headingMargin
        self.leftTextRect.left = self.backgroundRect.left + self.headingMargin

        self.rightTextImage = self.headingFont.render("Bug Injector", True, "white")
        self.rightTextRect = self.rightTextImage.get_rect()
        self.rightTextRect.top = self.backgroundRect.top + self.headingMargin
        self.rightTextRect.left = self.backgroundRect.left + self.backgroundRect.width / 2 + self.headingMargin

        # Problem Description
        self.textUiMargin = 10
        self.textUi = ui.ScrollableTextUi(
            pygame.Vector2(
                self.backgroundRect.left + self.textUiMargin,
                self.leftTextRect.bottom + self.textUiMargin
            ),
            self.backgroundRect.width / 2 - 2 * self.textUiMargin,
            self.backgroundRect.height - self.keyControls.rect.height - self.leftTextRect.height - 2 * self.textUiMargin,
            utils.load_font("SpaceMono/SpaceMono-Regular.ttf")
        )

        # Parsing Errors
        self.textFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf")
        self.set_error_text("")

        self.submitTime = None
        self.submitted = False
        self.solved = False
        self.isVisible = False
        self.on_close = on_close

        if TestCaseHackUi.showTutorial:
            EventManager.emit(
                EcodeEvent.GIVE_ORDER,
                text=
"""You've intercepted the attack algorithm of the boss you're fighting!
Bosses don't implement their attacks perfectly, though.
Defeat the boss by providing a test input which exposes its buggy implementation."""
            )
            TestCaseHackUi.showTutorial = False
        
        # Problem Information
        self.problem : Problem = ProblemFactory.create(problemSlug) 
        self.build_parameter_input()

        EventManager.emit(EcodeEvent.GET_PROBLEM_DESCRIPTION, problemSlug=problemSlug)
        EventManager.emit(EcodeEvent.PAUSE_GAME)
    
    def build_parameter_input(self):
        parameterInputMargin = 10
        self.parameterInput = ui.ParameterInputUi(
            self.backgroundRect.width / 2 - 2 * parameterInputMargin,
            pygame.Vector2(
                self.backgroundRect.left + self.backgroundRect.width / 2 + parameterInputMargin,
                self.rightTextRect.bottom + parameterInputMargin
            )
        )
        for parameter in self.problem.parameters:
            self.parameterInput.add_parameter(parameter)
        self.parameterInput.build()

    def set_problem_description(self, text: str):
        self.textUi.set_text(text)
        self.isVisible = True

    def set_error_text(self, text: str):
        self.errorTextImage = self.textFont.render(text, True, "red")
        self.errorTextRect = self.errorTextImage.get_rect()
        self.errorTextRect.bottomright = self.backgroundRect.bottomright
    
    def set_success_message(self, isHacked: bool):
        text = f"Exposed bug :P\n{self.problem.get_bug_explanation()}" if isHacked else "Failed to expose bug :O"
        color = "green" if isHacked else "red"
        self.successTextImage = self.textFont.render(text, True, color, wraplength=(self.backgroundRect.width // 2) - 2 * 10)
        self.successTextRect = self.successTextImage.get_rect()
        self.successTextRect.bottom = self.backgroundRect.bottom - 10
        self.successTextRect.left = self.textUi.scrollableContainer.rect.right + 10
    
    def close(self):
        self.isVisible = False
        self.on_close(TestCaseHackUi)
        EventManager.emit(EcodeEvent.UNPAUSE_GAME)
        if self.solved:
            EventManager.emit(EcodeEvent.KILL_BOSS)

    def handle_event(self, event: pygame.Event):
        if self.isVisible:
            self.textUi.handle_event(event)
            self.parameterInput.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                if event.key == pygame.K_RETURN and not self.submitted:
                    self.submitted = True
                    self.submitTime = pygame.time.get_ticks()
                    try: 
                        inputs = self.parameterInput.get_inputs()
                        if self.problem.check_input(**inputs):
                            self.solved = True
                            self.set_success_message(True)
                        else:
                            self.set_success_message(False)
                    except ValueError as e:
                        self.set_error_text(f"Error: {str(e)}")
        elif event.type == c.PROBLEM_DESCRIPTION:
            self.set_problem_description(BeautifulSoup(event.html, "html.parser").get_text())
    
    def update(self):
        if self.isVisible:
            self.textUi.update()
            self.keyControls.update()
            if not self.submitted:
                self.parameterInput.update()
            else:
                if not self.solved and pygame.time.get_ticks() - self.submitTime > 2000:
                    self.close()
                    
    def draw(self, surface: pygame.Surface):
        if self.isVisible:
            pygame.draw.rect(surface, 'blue', self.backgroundRect, border_radius=5)
            self.keyControls.draw(surface)
            self.textUi.draw(surface)
            self.parameterInput.draw(surface)
            surface.blit(self.errorTextImage, self.errorTextRect)
            surface.blit(self.leftTextImage, self.leftTextRect)
            surface.blit(self.rightTextImage, self.rightTextRect)
            if self.submitted:
                surface.blit(self.successTextImage, self.successTextRect)
                
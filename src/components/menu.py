import pygame
import sys
import requests
import json
import src.core.utils as utils
import src.config as config
import src.constants as c
from src.components.button import Button, TextInput

class Menu:
    """Base class for all menus in the game."""

    def __init__(self, manager):
        """Constructor.
        
            manager: The state manager driving the game.
        """
        self.manager = manager
        self.backgroundImage, _ = utils.load_png("menu_background.png")
        self.backgroundImage = pygame.transform.scale(self.backgroundImage, (c.SCREEN_HEIGHT, c.SCREEN_HEIGHT))
        self.controls = []

    def handle_event(self, event):
        """Handle discrete user input events."""
        [ctrl.handle_event(event) for ctrl in self.controls]

    def update(self):
        """Update the menu's state."""
        mouse_pos = pygame.mouse.get_pos()
        [ctrl.update(mouse_pos) for ctrl in self.controls]
    
    def draw(self, surface):
        """Draw the menu to the surface."""
        surface.blit(self.backgroundImage, (0, 0))
        [ctrl.draw(surface) for ctrl in self.controls]


class MainMenu(Menu):
    """Main menu for the game."""

    def __init__(self, manager):
        """Constructor.
        
            manager: The state manager driving the game.
        """
        super().__init__(manager)

        self.titleFont = utils.load_font("Monoton/Monoton-Regular.ttf", 60)
        self.titleTextImage = self.titleFont.render("EscapeCodes", True, "#bcbcbc")
        self.titleRect = self.titleTextImage.get_rect(center=(1000, 150))

        self.playImage, _ = utils.load_png("Play.png")
        self.optionImage, _ = utils.load_png("Play.png")
        self.quitImage, _ = utils.load_png("Play.png")
        self.controls += [
            Button(self.playImage, pos=(1000, 300), textInput="PLAY", onClick=self.onLogin),
            Button(self.optionImage, pos=(1000, 420), textInput="OPTIONS", onClick=self.onOption),
            Button(self.quitImage, pos=(1000, 540), textInput="QUIT", onClick=self.onQuit)
        ]
    
    def onOption(self):
        self.manager.set_state("options")
    
    def onLogin(self):
        self.manager.set_state("login")
    
    def onQuit(self):
        pygame.quit()
        sys.exit()

    def draw(self, surface):
        """Draw main menu to the surface."""
        super().draw(surface)
        surface.blit(self.titleTextImage, self.titleRect)


class OptionsMenu(Menu):
    """Options menu."""

    def __init__(self, manager):
        super().__init__(manager)
        self.backImage, _ = utils.load_png("Play.png")
        self.controls += [
            Button(self.backImage, pos=(640, 600), textInput="BACK", onClick=self.onBack)
        ]
    
    def onBack(self):
        self.manager.set_state("menu")

class LoginMenu(Menu):
    """Login menu."""

    def __init__(self, manager):
        super().__init__(manager)
        self.headingFont = pygame.font.SysFont("cambria", 40)
        self.headingTextImage = self.headingFont.render("Enter Your LeetCode Username", True, 'lightsalmon4')
        self.headingTextRect = self.headingTextImage.get_rect(center=(640, 300))
        self.backImage, _ = utils.load_png("Play.png")
        self.controls += [
            TextInput(pos=(540, 420), width=200, height=50, onSubmit=self.onEnter),
            Button(self.backImage, pos=(640, 600), textInput="BACK", onClick=self.onBack)
        ]

    def onBack(self):
        self.manager.set_state("menu")
    
    def onEnter(self, textInput):
        url = "https://leetcode-stats-api.herokuapp.com/" + textInput
        playerStats = json.loads(
            requests.get(
                url
            ).text
        )
        if playerStats["status"] == "success":
            self.manager.set_state("world")
            pygame.event.post(pygame.Event(c.USER_LOGIN, {"username": textInput, "stats": playerStats}))
    
    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.headingTextImage, self.headingTextRect)

class YouDiedMenu(Menu):
    """Menu that shows when player dies during level."""

    def __init__(self, manager):
        super().__init__(manager)
        self.retryImage, _ = utils.load_png("Play.png")
        self.quitImage, _ = utils.load_png("Play.png")
        self.controls += {
            Button(self.retryImage, pos=(640, 300), textInput="RETRY", onClick=self.onRetry),
            Button(self.quitImage, pos=(640, 420), textInput="QUIT", onClick=self.onQuit)
        }
    
    def onRetry(self):
        self.manager.set_state("world")
    
    def onQuit(self):
        self.manager.set_state("menu")
import pygame
import sys
import requests
import json
from pprint import pprint
import src.core.utils as utils
import src.config as config
import src.constants as c
from src.components.button import Button, TextInput, ToggleButton
from src.components.ui import KeyPromptControlBarUi, KeyPromptUi

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
        self.titleTextImage = self.titleFont.render("EscapeCodes", True, "white")
        self.titleRect = self.titleTextImage.get_rect(center=(1000, 150))

        self.playImage, _ = utils.load_png("Play.png")
        self.optionImage, _ = utils.load_png("Play.png")
        self.quitImage, _ = utils.load_png("Play.png")
        self.controls += [
            Button(self.playImage, pos=(1000, 300), textInput="Play", onClick=self.onLogin),
            Button(self.optionImage, pos=(1000, 420), textInput="Options", onClick=self.onOption),
            Button(self.quitImage, pos=(1000, 540), textInput="Quit", onClick=self.onQuit)
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
        self.headingFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)
        self.controls += [
            Button(self.backImage, pos=(1000, 540), textInput="Back", onClick=self.onBack)
        ]
        self.backImageRect = self.backImage.get_rect(center=(1000, 540))

        # background music + sound
        self.backgroundMusic = self.headingFont.render("Background Music", True, 'white')
        self.backgroundMusicRect = self.backgroundMusic.get_rect(center=(1000, 250))
        self.musicToggle = ToggleButton(pos=(1000,300))  # Near "Background Music"
        
        self.soundEffect = self.headingFont.render("Sound Effects", True, 'white')
        self.soundEffectRect = self.soundEffect.get_rect(center=(1000, 350))
        self.soundToggle = ToggleButton(pos=(1000, 400))  # Near "Sound Effects"
    
        self.controls += [self.musicToggle, self.soundToggle]

        # Controls
        self.backgroundRect = self.backgroundImage.get_rect()
        self.backgroundRect.inflate_ip(-20, -20)
        self.backgroundOverlay = pygame.Surface(self.backgroundRect.size, pygame.SRCALPHA).convert_alpha()

        self.optionControl = self.headingFont.render("Controls", True, 'white')
        self.optionControlRect = self.optionControl.get_rect(center=(self.backImageRect.left/2, 100))
        
        self.WASDControls = KeyPromptControlBarUi() # test main branch protection
        self.WASDControls.controls.clear()
        self.WASDControls.add_control(KeyPromptUi(pygame.K_w, "Keys/W-Key.png", caption="Move Up"))
        self.WASDControls.add_control(KeyPromptUi(pygame.K_a, "Keys/A-Key.png", caption="Move Left"))
        self.WASDControls.add_control(KeyPromptUi(pygame.K_s, "Keys/S-Key.png", caption="Move Down"))
        self.WASDControls.add_control(KeyPromptUi(pygame.K_d, "Keys/D-Key.png", caption="Move Right"))
        self.WASDControls.build()
        self.WASDControls.rect.center = (
            self.backImageRect.left/2, 200
        )
        
        self.QEPControls = KeyPromptControlBarUi()
        self.QEPControls.controls.clear()
        self.QEPControls.add_control(KeyPromptUi(pygame.K_q, "Keys/Q-Key.png", caption="Zoom In"))
        self.QEPControls.add_control(KeyPromptUi(pygame.K_e, "Keys/E-Key.png", caption="Zoom Out"))
        self.QEPControls.add_control(KeyPromptUi(pygame.K_p, "Keys/P-Key.png", caption="Punch"))
        self.QEPControls.build()
        self.QEPControls.rect.center = (
            self.backImageRect.left/2, 300
        )

        self.SpaceControls = KeyPromptControlBarUi()
        self.SpaceControls.controls.clear()
        self.SpaceControls.add_control(KeyPromptUi(pygame.K_SPACE, "Keys/Space-Key.png", fileMetadata=c.LG_KEY_SHEET_METADATA, caption="Dash"))
        self.SpaceControls.build()
        self.SpaceControls.rect.center = (
            self.backImageRect.left/2, 400
        )

        self.backgroundRect.centerx = self.WASDControls.rect.centerx + 20

    def update(self):
        self.WASDControls.update()
        self.QEPControls.update()
        self.SpaceControls.update()

    def onBack(self):
        self.manager.set_state("menu")

    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        pygame.draw.rect(self.backgroundOverlay, (73, 73, 73, 150), self.backgroundRect)
        surface.blit(self.backgroundOverlay)
        surface.blit(self.backgroundMusic, self.backgroundMusicRect)
        surface.blit(self.soundEffect, self.soundEffectRect)
        surface.blit(self.optionControl, self.optionControlRect)
        self.musicToggle.draw(surface)
        self.soundToggle.draw(surface)
        self.WASDControls.draw(surface)
        self.QEPControls.draw(surface)
        self.SpaceControls.draw(surface)

class LoginMenu(Menu):
    """Login menu."""

    def __init__(self, manager):
        super().__init__(manager)
        self.headingFont = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)
        self.headingTextImage = self.headingFont.render("Enter Your LeetCode Username", True, 'white')
        self.headingTextRect = self.headingTextImage.get_rect(center=(1000, 250))
        self.errorTextImage = self.headingFont.render("Error: not a valid username", True, 'red')
        self.errorTextRect = self.errorTextImage.get_rect(center=(1000, 450))
        self.showError = False
        self.backImage, _ = utils.load_png("Play.png")
        self.controls += [
            TextInput(pos=(1000, 370), width=200, height=45, onSubmit=self.onEnter),
            Button(self.backImage, pos=(1000, 540), textInput="Back", onClick=self.onBack)
        ]

    def onBack(self):
        self.manager.set_state("menu")
    
    def onEnter(self, textInput):
        url = "https://leetcode.com/graphql"
        headers = {
            "Content-Type": "application/json"
        }
        query = """
        query skillStats($username: String!) {
            matchedUser(username: $username) {
                tagProblemCounts {
                    advanced {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    intermediate {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    fundamental {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                }
            }
        }
        """
        variables = {
            "username": textInput
        }
        response = requests.post(
            url,
            json={
                "query": query,
                "variables": variables,
                "headers": headers
            }
        )
        print(f"Validating username {textInput}")
        if response.status_code == 200:
            data = response.json()["data"]
            pprint(data)
            if data["matchedUser"] is None:
                print(f"\tInvalid username: {textInput}")
                self.showError = True
            else:
                self.manager.set_state("intro")
                pygame.event.post(pygame.Event(c.USER_LOGIN, {"username": textInput, "stats": json.loads(response.text)}))
        else:
            print(f"\tInvalid username: {textInput}")
            self.showError = True
    
    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.headingTextImage, self.headingTextRect)
        if self.showError:
            surface.blit(self.errorTextImage, self.errorTextRect)

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
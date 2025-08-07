import pygame
from src.core.game import Game
from src.core.leetcodeManager import LeetcodeManager
from src.components.menu import MainMenu, OptionsMenu, LoginMenu, YouDiedMenu, PauseMenu
from src.components.levelsMenu import LevelsMenu
from src.components.ui import KeyPromptUi
import src.core.utils as utils
import src.constants as c


class GameStates:
    Menu = "menu"
    Options = "options"
    Pause = "pause"
    Login = "login"
    Intro = "intro"
    World = "world"
    Died = "died"
    Levels = "levels"


class GameManager:
    def __init__(self):
        self.states = {
            GameStates.Menu: MainMenu,
            GameStates.Options: OptionsMenu,
            GameStates.Pause: PauseMenu,
            GameStates.Login: LoginMenu,
            GameStates.Intro: TextSlideShow,
            GameStates.World: self.get_current_level,
            GameStates.Levels: LevelsMenu,
            GameStates.Died: YouDiedMenu
        }
        self.leetcodeManager = LeetcodeManager()
        self.level_idx = 0
        self.gameInstance : Game = None
        self.num_unlocked = 0

        self.set_state(GameStates.Login)
       
        
    def get_current_level(self):
        return Game(self, level_index=self.level_idx)

    def set_state(self, stateName):
        pygame.display.set_caption(stateName)
        if stateName == GameStates.World:
            self.gameInstance = self.states[GameStates.World]()
            self.activeState = self.gameInstance
        else:
            self.activeState = self.states[stateName](self) 
    
    def quit_game(self):
        if self.gameInstance:
            self.gameInstance.quit()
            self.gameInstance = None

    def handle_event(self, event):
        self.activeState.handle_event(event)
        self.leetcodeManager.handle_event(event)

    def update(self):
        self.activeState.update()

    def draw(self, screen):
        self.activeState.draw(screen)

    def unlocked(self, unlocked_idx):
        self.num_unlocked = unlocked_idx

class TextSlideShow:
    def __init__(self, manager):
        """Constructor."""
        self.manager = manager
        self.lines = [
"""2032:
First permanent colony and fully-automated mining venture established on Mars by tech conglomerate WeX.
A bidding war for prime real estate begins amongst the company's top executives.""",
"""2035:
The universe's most incredible travel destinations are unlocked.
The Utopia, an one-of-a-kind vessel, announces its passage from Earth to Mars, intended to host neo-settlers and start-ups alike.""",
"""2041:
The Earth bleeds, wrought by man-made fires, crumbling infrastructure, and worn reserves of nearly everything needed to sustain human life.
There are no more resources: a planet in revolt. It is time to go.""",
"""2042 (Present):
You are a technician tasked with checking the Utopia before the expedition, preparing for an unforgettable trip to the New World.""" 
        ]
        self.line = 0
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 30)
        self.font2 = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", 20)
        self.margin = 100
        self.render_text()
    
    def render_text(self):        
        self.textImage = self.font.render(
            self.lines[self.line],
            True,
            "white",
            wraplength=c.SCREEN_WIDTH - 2 * self.margin
        )
        self.textRect = self.textImage.get_rect()
        self.textRect.centerx = c.SCREEN_WIDTH // 2
        self.textRect.centery = c.SCREEN_HEIGHT // 2

        self.nextKeyPromptUi = KeyPromptUi(pygame.K_d, "Keys/D-Key.png", caption="Next")
        self.backKeyPromptUi = KeyPromptUi(pygame.K_a, "Keys/A-Key.png", caption="Back")

        self.nextKeyPromptUi.rect.bottom = c.SCREEN_HEIGHT - 10
        self.nextKeyPromptUi.rect.right = c.SCREEN_WIDTH - 10
        self.backKeyPromptUi.rect.bottom = self.nextKeyPromptUi.rect.bottom
        self.backKeyPromptUi.rect.right = self.nextKeyPromptUi.rect.left - 10

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.nextKeyPromptUi.key:
                self.line += 1
                if self.line >= len(self.lines):
                    self.manager.set_state("world")
                    return
            elif event.key == self.backKeyPromptUi.key:
                self.line = max(0, self.line - 1)
            self.render_text()
    
    def update(self):
        self.nextKeyPromptUi.update()
        self.backKeyPromptUi.update()

    def draw(self, screen):
        screen.blit(self.textImage, self.textRect)
        self.nextKeyPromptUi.draw(screen)
        self.backKeyPromptUi.draw(screen)
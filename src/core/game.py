from src.core.camera import Camera
from src.core.leetcodeManager import LeetcodeManager
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.core.uiManager import UiManager
from src.core.level import Level
from src.levels.tutorial import Tutorial, Level1
import src.constants as c

class Game():
    """Manages high-level gameplay logic like switching between levels and camera functions."""
   
    def __init__(self, manager, playerStats):
        self.manager = manager
        self.camera = Camera()
        self.leetcodeManager = LeetcodeManager()
        self.uiManager = UiManager()
        self.levels: list[Level] = [
            Tutorial(),
            Level1("level1.png", "level1.tmj"),
            Level("level2.png", "level2.tmj")
        ]
        self.level = 0
        self.levels[self.level].load_camera(self.camera)
        self.isPaused = False

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.PAUSE_GAME, self.pause)
        EventManager.subscribe(EcodeEvent.UNPAUSE_GAME, self.unpause)

    def pause(self):
        self.isPaused = True
    
    def unpause(self):
        self.isPaused = False

    def update(self):
        if not self.isPaused:
            self.levels[self.level].update()
            self.camera.update()
        self.leetcodeManager.update()
        self.uiManager.update()
    
    def next_level(self):
        self.camera.reset()
        if self.level == len(self.levels) - 1:
            self.level = 0
            self.manager.set_state("menu")
        else:
            self.level += 1
        self.levels[self.level].load_camera(self.camera)

    def handle_event(self, event):
        if not self.isPaused:
            self.levels[self.level].handle_event(event)
            self.camera.handle_event(event)
        
            if event.type == c.LEVEL_ENDED:
                self.camera.reset()
                self.next_level()
            elif event.type == c.PLAYER_DIED:
                self.camera.reset()
                self.levels[self.level].reset(self.camera)
                self.manager.set_state("died")
        
        self.leetcodeManager.handle_event(event)
        self.uiManager.handle_event(event)
        
        

    def draw(self, surface):
        self.camera.draw(surface)
        self.uiManager.draw(surface)

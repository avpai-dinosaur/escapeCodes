from src.core.camera import Camera
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.core.uiManager import UiManager
from src.core.level import LevelFactory 
import src.constants as c


class Game():
    """Manages high-level gameplay logic like switching between levels and camera functions."""
   
    def __init__(self, manager, playerStats):
        self.manager = manager
        self.camera = Camera()
        self.uiManager = UiManager()
        self.levels: list[str] = [
            "tutorial",
            "level1",
            "level2",
            "level3"
        ]
        self.currentLevelIdx = -1
        self.isPaused = False
        self.next_level()

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.PAUSE_GAME, self.pause)
        EventManager.subscribe(EcodeEvent.UNPAUSE_GAME, self.unpause)
        EventManager.subscribe(EcodeEvent.PLAYER_DIED, self.on_death)
        EventManager.subscribe(EcodeEvent.LEVEL_ENDED, self.next_level)

    def pause(self):
        self.isPaused = True
    
    def unpause(self):
        self.isPaused = False

    def on_death(self):
        self.camera.reset()
        self.currentLevel.reset(self.camera)
        self.manager.set_state("died")

    def update(self):
        if not self.isPaused:
            self.currentLevel.update()
            self.camera.update()
        self.uiManager.update()
        EventManager.update()
    
    def next_level(self):
        self.camera.reset()
        if self.currentLevelIdx == len(self.levels) - 1:
            self.currentLevelIdx = -1
            self.manager.set_state("menu")
        else:
            self.currentLevelIdx += 1
        self.currentLevel = LevelFactory.create(self.levels[self.currentLevelIdx])
        self.currentLevel.load_camera(self.camera)

    def handle_event(self, event):
        if not self.isPaused:
            self.currentLevel.handle_event(event)
            self.camera.handle_event(event)
        
        self.uiManager.handle_event(event)

    def draw(self, surface):
        self.camera.draw(surface)
        self.uiManager.draw(surface)

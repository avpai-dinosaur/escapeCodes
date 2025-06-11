from src.core.camera import Camera
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.core.uiManager import UiManager
from src.core.level import LevelFactory 
import src.constants as c


class Game():
    """Manages high-level gameplay logic like switching between levels and camera functions."""

    currentLevelIdx = None
   
    def __init__(self, manager):
        self.manager = manager
        self.camera = Camera()
        self.uiManager = UiManager()
        self.levels: list[str] = [
            "tutorial",
            "level1",
            "level2",
            "level3"
        ]
        self.isPaused = False

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.PAUSE_GAME, self.pause)
        EventManager.subscribe(EcodeEvent.UNPAUSE_GAME, self.unpause)
        EventManager.subscribe(EcodeEvent.PLAYER_DIED, self.on_death)
        EventManager.subscribe(EcodeEvent.LEVEL_ENDED, self.on_level_end)
        EventManager.subscribe(EcodeEvent.NEXT_LEVEL, self.next_level)

        self.next_level()

    def pause(self):
        self.isPaused = True
    
    def unpause(self):
        self.isPaused = False

    def on_death(self):
        self.camera.reset()
        self.currentLevel.reset(self.camera)
        Game.currentLevelIdx -= 1 # Get back to the same level if player retries
        self.destroy()
        self.manager.set_state("died")
    
    def on_level_end(self):
        self.currentLevel.end_level()

    def destroy(self):
        EventManager.unsubscribe(EcodeEvent.PAUSE_GAME, self.pause)
        EventManager.unsubscribe(EcodeEvent.UNPAUSE_GAME, self.unpause)
        EventManager.unsubscribe(EcodeEvent.PLAYER_DIED, self.on_death)
        EventManager.unsubscribe(EcodeEvent.LEVEL_ENDED, self.on_level_end)
        EventManager.unsubscribe(EcodeEvent.NEXT_LEVEL, self.next_level)

    def update(self):
        if not self.isPaused:
            self.currentLevel.update()
        self.camera.update()
        self.uiManager.update()
        EventManager.update()
    
    def next_level(self):
        self.camera.reset()
        if Game.currentLevelIdx is None:
            Game.currentLevelIdx = 0
        elif Game.currentLevelIdx == len(self.levels) - 1:
            Game.currentLevelIdx = None
            self.destroy()
            self.manager.set_state("menu")
            return
        else:
            Game.currentLevelIdx += 1
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

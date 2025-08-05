from src.core.camera import Camera
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.core.uiManager import UiManager
from src.core.level import LevelFactory, Level 


class Game():
    """Manages high-level gameplay logic like switching between levels and camera functions."""
   
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
        self.currentLevelIdx = 0
        self.currentLevel: Level = LevelFactory.create(self.levels[self.currentLevelIdx])
        self.currentLevel.load_camera(self.camera)

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.PAUSE_GAME, self.pause)
        EventManager.subscribe(EcodeEvent.UNPAUSE_GAME, self.unpause)
        EventManager.subscribe(EcodeEvent.PLAYER_DIED, self.on_death)
        EventManager.subscribe(EcodeEvent.LEVEL_ENDED, self.next_level)
        EventManager.subscribe(EcodeEvent.PAUSE_MENU, self.pause_menu)

    def pause(self):
        self.isPaused = True
    
    def unpause(self):
        self.isPaused = False

    def on_death(self):
        self.end_current_level()
        self.load_current_level()
        self.manager.set_state("died")
    
    def next_level(self):
        self.end_current_level()
        self.currentLevelIdx += 1
        if self.currentLevelIdx == len(self.levels):
            self.currentLevelIdx = 0
            self.manager.set_state("menu")
        self.load_current_level()

    def load_current_level(self):
        self.currentLevel = LevelFactory.create(self.levels[self.currentLevelIdx])
        self.currentLevel.load_camera(self.camera)

    def end_current_level(self):
        self.camera.reset()
        self.currentLevel.destroy()
        self.currentLevel = None
    
    def quit(self):
        self.end_current_level()
        self.camera.destroy()
        EventManager.unsubscribe(EcodeEvent.PAUSE_GAME, self.pause)
        EventManager.unsubscribe(EcodeEvent.UNPAUSE_GAME, self.unpause)
        EventManager.unsubscribe(EcodeEvent.PLAYER_DIED, self.on_death)
        EventManager.unsubscribe(EcodeEvent.LEVEL_ENDED, self.next_level)
        EventManager.unsubscribe(EcodeEvent.PAUSE_MENU, self.pause_menu)
    
    def pause_menu(self):
        self.manager.set_state("pause")

    def update(self):
        if not self.isPaused:
            self.currentLevel.update()
        self.camera.update()
        self.uiManager.update()
        EventManager.update()
    
    def handle_event(self, event):
        if not self.isPaused:
            self.currentLevel.handle_event(event)
            self.camera.handle_event(event)
        
        self.uiManager.handle_event(event)

    def draw(self, surface):
        self.camera.draw(surface)
        self.uiManager.draw(surface)

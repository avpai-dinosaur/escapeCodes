import pygame
from collections import deque
from src.core.camera import Camera
from src.entities.player import Player
from src.entities.roomba import Roomba
from src.entities.boss import Druck
from src.core.map import Map
from src.components.ui import StandAloneKeyPromptUi
import src.core.utils as utils
import src.constants as c
from src.core.ecodeEvents import EventManager, EcodeEvent


class Level():
    """Represents a level in the game."""

    def __init__(self, imageFile: str, dataFile: str):
        self.map = Map(imageFile, dataFile)
        self.load_entities()
        self.start_level()

    def load_entities(self):
        self.objects = self.map.object_factory()
        self.walls = self.map.walls_factory()
        self.rooms, self.bossRoom = self.map.rooms_factory()
        self.doors = self.map.doors_factory()

        self.player = Player("Oldhero.png", self.map.playerSpawn, {})
        self.entities = pygame.sprite.Group()
        if self.bossRoom:
            boss = Druck(
                self.bossRoom,
                "two-sum"
            )
            self.entities.add(boss)
        if self.map.roombaPath:
            roomba = Roomba("roomba.png", self.map.roombaPath)
            self.set_roomba_dialog(roomba)
            self.entities.add(roomba)
    
    def set_roomba_dialog(self, roomba):
        pass

    def load_camera(self, camera: Camera):
        camera.add(self.player)
        camera.add(self.entities)
        camera.add(self.objects)
        camera.add(self.doors)

        # camera.background_objects.add(self.map.background_objects)

        camera.target = self.player.rect
        camera.background = self.map.image
    
    def start_level(self):
        pass
    
    def reset(self, camera):
        self.load_entities()
        self.load_camera(camera)

    def end_level(self):
        EventManager.emit(EcodeEvent.NEXT_LEVEL)
    
    def player_died(self):
        # TODO: the player should probably post this event
        pygame.event.post(pygame.event.Event(c.PLAYER_DIED))

    def update(self):
        self.player.update(self.walls, self.doors)
        self.entities.update(self.player)
        self.doors.update(self.player)
        self.objects.update(self.player)
        
        # self.map.background_objects.update(self.player)
    
    def handle_event(self, event):
        # TODO: This is not that great of a solution. 
        # We need a custom class that inherits from Sprite group 
        # which has a handle_event method and we need to add
        # our objects to that custom group.
        # Every object should also probably have a handle event method
        # and they should inheret from a base object
        for obj in self.objects:
            handleEventOp = getattr(obj, "handle_event", None)
            if callable(handleEventOp):
                handleEventOp(event)

        for entity in self.entities:
            handleEventOp = getattr(entity, "handle_event", None)
            if callable(handleEventOp):
                handleEventOp(event)

        [d.handle_event(event) for d in self.doors]

        if event.type == pygame.KEYDOWN:
            # if event.key == pygame.K_ESCAPE:
            #     self.end_level()
            # TODO: This is just for testing purposes
            if event.key == pygame.K_v:
                self.player_died()
    
    def draw_ui(self, surface):
        """Draw any ui specific to the level."""
        pass


class LevelFactory():
    """Maps level names to the level class."""
    _registry = {}

    def register(levelName: str, levelClass) -> None:
        if levelName in LevelFactory._registry:
            raise ValueError(f"Level {levelName} already registered")
        LevelFactory._registry[levelName] = levelClass
    
    def create(levelName: str) -> Level:
        if levelName not in LevelFactory._registry:
            raise ValueError(f"Level '{levelName}' not found")
        return LevelFactory._registry[levelName]()
    
    def register_level(levelName):
        def decorator(levelClass):
            LevelFactory.register(levelName, levelClass)
            return levelClass
        return decorator


@LevelFactory.register_level("tutorial")
class Tutorial(Level):
    def __init__(self):
        super().__init__("level0.png", "level0.tmj")
        self.keyPromptEvents = deque()
        self.keyPromptEvents.append(
            (
                EcodeEvent.OPEN_WASD,
                [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d],
                {}
            )
        )
        self.keyPromptEvents.append(
            (
                EcodeEvent.OPEN_KEY_PROMPT,
                [pygame.K_q],
                {
                    "key": pygame.K_q,
                    "filename": "Keys/Q-Key.png",
                    "fileMetadata": c.SM_KEY_SHEET_METADATA,
                    "caption": "Zoom In"
                }
            )
        )
        self.keyPromptEvents.append(
            (
                EcodeEvent.OPEN_KEY_PROMPT,
                [pygame.K_e],
                {
                    "key": pygame.K_e, 
                    "filename": "Keys/E-Key.png", 
                    "fileMetadata": c.SM_KEY_SHEET_METADATA, 
                    "caption": "Zoom Out"
                }
            )
        )
        self.keyPromptEvents.append(
            (
                EcodeEvent.OPEN_KEY_PROMPT,
                [pygame.K_p],
                {
                    "key": pygame.K_p,
                    "filename": "Keys/P-Key.png",
                    "fileMetadata": c.SM_KEY_SHEET_METADATA,
                    "caption": "Punch"
                }
            )
        )
        self.keyPromptEvents.append(
            (
                EcodeEvent.OPEN_KEY_PROMPT,
                [pygame.K_SPACE],
                {
                    "key": pygame.K_SPACE,
                    "filename": "Keys/Space-Key.png",
                    "fileMetadata": c.LG_KEY_SHEET_METADATA,
                    "caption": "Dash"
                }
            )
        )
        self.currentKeys = None
        self.next_key_prompt()
    
    def next_key_prompt(self):
        if len(self.keyPromptEvents) > 0:
            event, self.currentKeys, eventArgs = self.keyPromptEvents.popleft()
            EventManager.emit(event, **eventArgs)

    def start_level(self):
        EventManager.emit(
            EcodeEvent.GIVE_ORDER,
            text="Go to the bridge of the Utopia and perform a routine check of the ship's functionality."
        )
    
    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pygame.KEYDOWN:
            if self.currentKeys and event.key in self.currentKeys:
                self.next_key_prompt()
                
    def end_level(self):
        cameraShakeDuration = 5000
        EventManager.emit(EcodeEvent.CAMERA_SHAKE, duration=cameraShakeDuration, maxIntensity=10)
        EventManager.emit(EcodeEvent.NEXT_LEVEL, delay=cameraShakeDuration)


@LevelFactory.register_level("level1")
class Level1(Level):
    def __init__(self):
        super().__init__("level1.png", "level1.tmj")

    def set_roomba_dialog(self, roomba: Roomba):
        roomba.set_dialog(
            [
"""Remnants of a celebration detected.
Joy levels: high.
Cleanliness levels: catastrophic.
Initiating deep clean protocol.
Estimated time to completion: eternal""",
"""Glitter.
You people know glitter is forever, right?
Even I can't find it all, and I'm a sentient dirt radar.""",
"""I detect...sticky. So much sticky.
What is this, pop? Juice? A melted popsicle?
I wasn't built for this level of betrayal.""",
"""In need of cleaning solution refueling. Desperation levels: high."""
            ]
        )
    
    def start_level(self):
        blackoutDuration = 10000
        EventManager.emit(EcodeEvent.CAMERA_BLACKOUT, duration=blackoutDuration)
        EventManager.emit(
            EcodeEvent.GIVE_ORDER,
            delay=blackoutDuration,
            text="ERR: Unable To Find Objective"
        )


@LevelFactory.register_level("level2")
class Level2(Level):
    def __init__(self):
        super().__init__("level2.png", "level2.tmj")
    
    def start_level(self):
        EventManager.emit(
            EcodeEvent.GIVE_ORDER,
            text="Hello? HELLO?"
        )


@LevelFactory.register_level("level3")
class Level3(Level):
    def __init__(self):
        super().__init__("level3.png", "level3.tmj")
    
    def start_level(self):
        EventManager.emit(
            EcodeEvent.GIVE_ORDER,
            text="Turn back if you can here me. Do not go that way!"
        )
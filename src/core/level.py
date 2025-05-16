import pygame
from src.core.camera import Camera
from src.entities.player import Player
from src.entities.roomba import Roomba
from src.entities.boss import Druck
from src.core.map import Map
import src.core.utils as utils
import src.constants as c

class Level():
    """Represents a level in the game."""

    def __init__(self, imageFile: str, dataFile: str):
        self.map = Map(imageFile, dataFile)
        self.load_entities()

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
            self.entities.add(roomba)
    
    def load_camera(self, camera: Camera):
        camera.add(self.player)
        camera.add(self.entities)
        camera.add(self.objects)
        camera.add(self.doors)

        # camera.background_objects.add(self.map.background_objects)

        camera.target = self.player.rect
        camera.background = self.map.image
    
    def reset(self, camera):
        self.load_entities()
        self.load_camera(camera)

    def end_level(self):
        pygame.event.post(pygame.event.Event(c.LEVEL_ENDED))
    
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
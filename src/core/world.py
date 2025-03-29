import pygame
from src.core.camera import Camera
from src.core.problemManager import LeetcodeManager
from src.entities.player import Player
from src.entities.roomba import Roomba
from src.core.map import Map
import constants as c

class Level():
    """Represents a level in the game."""

    def __init__(self, map: Map):
        self.map = map
        self.load_entities()

    def load_entities(self):
        self.player = Player("data/images/Oldhero.png", self.map.playerSpawn, {})
        self.roomba = Roomba("data/images/roomba.png", self.map.roombaPath)
        self.objects = self.map.object_factory()
        self.walls = self.map.walls_factory()
        self.doors = self.map.doors_factory()

    def load_camera(self, camera: Camera):
        camera.add(self.player)
        camera.add(self.roomba)
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
        self.roomba.update(self.player)
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
            if event.key == pygame.K_ESCAPE:
                self.end_level()
            # TODO: This is just for testing purposes
            if event.key == pygame.K_v:
                self.player_died()

class Game():
    """Manages high-level gameplay logic like switching between levels and camera functions."""
   
    def __init__(self, manager, playerStats):
        self.manager = manager
        self.camera = Camera()
        self.leetcodeManager = LeetcodeManager()
        self.levels = [
            Level(Map("data/images/level1.png", "data/map/level1.tmj")),
            Level(Map("data/images/level2.png", "data/map/level2.tmj"))
        ]
        self.level = 0
        self.levels[self.level].load_camera(self.camera)

    def update(self):
        self.levels[self.level].update()
        self.camera.update()
        self.leetcodeManager.update()
    
    def next_level(self):
        self.camera.reset()
        if self.level == len(self.levels) - 1:
            self.level = 0
            self.manager.set_state("menu")
        else:
            self.level += 1
        self.levels[self.level].load_camera(self.camera)

    def handle_event(self, event):
        self.levels[self.level].handle_event(event)
        self.camera.handle_event(event)
        self.leetcodeManager.handle_event(event)
        if event.type == c.LEVEL_ENDED:
            self.camera.reset()
            self.next_level()
        elif event.type == c.PLAYER_DIED:
            self.camera.reset()
            self.levels[self.level].reset(self.camera)
            self.manager.set_state("died")

    def draw(self, surface):
        self.camera.draw(surface)

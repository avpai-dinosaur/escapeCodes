import pygame
from src.entities.boss import Boss
from src.core.level import Level
import src.constants as c

class Tutorial(Level):
    def __init__(self):
        super().__init__("level0.png", "level0.tmj")

class Level1(Level):
    def load_entities(self):
        super().load_entities()
        roomRect = pygame.Rect(
            39 * c.TILE_SIZE,
            2 * c.TILE_SIZE,
            11 * c.TILE_SIZE,
            17 * c.TILE_SIZE
        )
        boss = Boss(pygame.Vector2(2560, 256), roomRect, "two-sum")
        self.entities = pygame.sprite.Group(boss)
    
    def load_camera(self, camera):
        super().load_camera(camera)
        camera.add(self.entities)

    def update(self):
        super().update()
        self.entities.update(self.player)

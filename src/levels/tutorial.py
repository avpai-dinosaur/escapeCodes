import pygame
from random import randint
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.core.level import Level
import src.constants as c

class Tutorial(Level):
    def __init__(self):
        super().__init__("level0.png", "level0.tmj")

class Level1(Level):
    def __init__(self, imageFile, dataFile):
        super().__init__(imageFile, dataFile)
        self.triggeredMovingBarUi = False

    def load_entities(self):
        super().load_entities()
        self.boss = Boss(pygame.Vector2(2560, 256))
    
    def load_camera(self, camera):
        super().load_camera(camera)
        camera.add(self.boss)
    
    def update(self):
        super().update()
        if self.boss.rect.colliderect(self.player.rect):
            self.player.health.lose(1)
        if self.boss.rect.inflate(30, 30).colliderect(self.player.rect) and not self.triggeredMovingBarUi:
            EventManager.emit(EcodeEvent.OPEN_BAR)
        self.boss.update()
    

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2):
        super().__init__()
        self.pos = pos
        self.rect = pygame.Rect(pos.x, pos.y, 64 * 3, 64 * 3)
        self.speed = 10
        self.get_next_pos()
    
    def get_next_pos(self):
        x = randint(39, 49 - 3)
        y = randint(3, 18 - 3)
        self.nextPos = pygame.Vector2(x * c.TILE_SIZE, y * c.TILE_SIZE)

    def move(self, target: pygame.Vector2):
        """Move enemy to the target point.

        Returns true if target was reached.
        
            target: Vector2.
        """
        reached = False
        movement = target - self.pos
        distance = movement.length()

        if movement[0] < 0:
            self.face_right = False
        elif movement[0] == 0:
            pass
        else:
            self.face_right = True

        if distance >= self.speed:
            self.pos += movement.normalize() * self.speed
        else:
            if distance != 0:
                self.pos += movement.normalize() * distance
            reached = True
        self.rect.topleft = self.pos
        return reached
    
    def update(self):
        if (self.move(self.nextPos)):
            self.get_next_pos()

    def draw(self, surface, offset):
        pygame.draw.rect(surface, "red", self.rect.move(offset[0], offset[1]), border_radius=10)


    

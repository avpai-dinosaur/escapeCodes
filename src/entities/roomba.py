import pygame
import src.core.utils as utils
import src.constants as c
import src.entities.objects as o
from src.core.spritesheet import SpriteSheet
from enum import Enum


class Roomba(pygame.sprite.Sprite):
    """Class to represent the roomba player encounters in Level 1."""

    class MoveState(Enum):
        """State of the enemy's movement."""
        STOP = 0
        PATH = 1
        PAUSE = 2
    
    def __init__(self, image, path):
        """Constructor.

            path: List of Vector2 objects specifying path along 
                  which the roomba will walk.
            image: roomba sprite PNG file.
        """
        super().__init__()

        # Animation Variables
        # self.spritesheet = SpriteSheet(image, c.ENEMY_SHEET_METADATA)
        self.action = "walk"
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.cooldown = 100
        
        # Image variables
        og_image, _ = utils.load_png(image)
        self.image = pygame.transform.scale(og_image, (72, 72))

        # self.image = self.spritesheet.get_image(self.action, self.current_frame)
        self.rect = self.image.get_rect()
        self.face_right = True

        # Roomba's Move state
        self.move_state = Roomba.MoveState.STOP

        # Path following
        self.path = path
        self.pos = self.path[0].copy() # This NEEDS to be a copy to avoid modifying path!
        self.rect.center = self.pos
        self.target_point = 1
        self.target = self.path[self.target_point]
        self.direction = 1

        # Roomba characteristics
        self.speed = c.ENEMY_SPEED

        # Speech Bubble
        self.speech = o.SpeechBubble(
            "humans are slobs...",
            pygame.font.Font(None, 36),
            (255, 255, 255),
            (0, 0, 0),
            self.rect.midtop
        )
        self.half_width = self.rect.width

    def update(self, player):
        """Update function to run each game tick.
        
        Roomba should wait until player opens near door, follow cleaning path,
        then wait until player opens far door before entering Zuck's room. 

            player: the player object.
        """
        if self.move_state == Roomba.MoveState.STOP:
            if pygame.Rect.colliderect(self.rect, player.rect):
                self.move_state = Roomba.MoveState.PATH
        elif self.move_state == Roomba.MoveState.PATH:
            if self.move(self.target):
                if self.target_point == len(self.path) - 1:
                    self.move_state = Roomba.MoveState.STOP
                    self.speech.update_text(
                        "Hey you!\nOpen this door, I need more cleaning supplies."
                    )
                        
                else:
                    self.target_point += 1
                    self.target = self.path[self.target_point]
            if pygame.Rect.colliderect(self.rect, player.rect):
                self.move_state = Roomba.MoveState.PAUSE
                self.speech.toggle = True
        elif self.move_state == Roomba.MoveState.PAUSE:
            if not pygame.Rect.colliderect(self.rect, player.rect):
                self.move_state = Roomba.MoveState.PATH
                self.speech.toggle = False
        
        self.speech.update_pos(self.rect.midtop)
        # self.update_animation()

    def update_animation(self):
        """Update animation of enemy."""
        current_time = pygame.time.get_ticks()
        if(current_time - self.last_update >= self.cooldown):
            #if animation cooldown has passed between last update and current time, switch frame
            self.current_frame += 1
            self.last_update = current_time
            
            #reset frame back to 0 so it doesn't index out of bounds
            if(self.current_frame >= self.spritesheet.num_frames(self.action)):
                self.current_frame = 0
            
            self.image = pygame.transform.flip(
                self.spritesheet.get_image(self.action, self.current_frame), 
                self.face_right,
                False
            )

    def move(self, target):
        """Move roomb to the target point.

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
        
        self.rect.center = self.pos
        
        return reached

    def draw(self, surface, offset):
        self.speech.draw(surface, offset)
        surface.blit(self.image, self.rect.topleft + offset)
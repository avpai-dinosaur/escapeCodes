import pygame
import utils
from spritesheet import SpriteSheet
import constants as c


class HealthBar():
    """Represents the player's healthbar."""
    def __init__(self,x,y,w,h,max_hp):
        self.x = x 
        self.y = y
        self.w = w 
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp
    
    def draw(self, surface):
        self.hp -= 0.01
        ratio = self.hp/self.max_hp
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))
        

class Player(pygame.sprite.Sprite):
    """Represents the player."""

    def __init__(self, filename, pos):
        """Constructor.

            filename: location of png image of the player
            pos: tuple representing players inital position
        """
        super().__init__()
        self.health = HealthBar(pos[0], pos[1], 60, 10, 100)
        self.speed = 0.01
        self.pos = pygame.Vector2(pos)
        self.spritesheet = SpriteSheet(filename, c.PLAYER_SHEET_METADATA)
        
        # Animation variables
        self.last_update = pygame.time.get_ticks()
        self.current_frame = 0
        self.action = "idle"
        self.face_left = False
        
        self.image = self.spritesheet.get_image(self.action, self.current_frame)
        self.rect = self.image.get_rect()
        self.rect.center = pos
    
    def update(self, walls, doors):
        """Updates the player's position."""
        new_pos = pygame.Vector2(self.pos)

        keys = pygame.key.get_pressed()
        self.action = "idle"
        if keys[pygame.K_w]:
            new_pos.y = self.pos.y - 150 * self.speed
            self.action = "run"
        if keys[pygame.K_s]:
            new_pos.y = self.pos.y + 150 * self.speed
            self.action = "run"
        if keys[pygame.K_a]:
            new_pos.x = self.pos.x - 150 * self.speed
            self.action = "run"
            self.face_left = True
        if keys[pygame.K_d]:
            new_pos.x = self.pos.x + 150 * self.speed
            self.action = "run"
            self.face_left = False
        # Redo to have these play all the way out
        if keys[pygame.K_i]:
            self.action = "punch"
        if keys[pygame.K_k]:
            self.action = "kick"
        if keys[pygame.K_SPACE]:
            self.action = "jump"
        
        # tentatively update to the new position
        # might have to undo if it turns out new position
        # collides with a barrier
        self.rect.center = new_pos

        # check if the proposed position collides with walls
        for wall in walls:
            if pygame.Rect.colliderect(wall, self.rect):
                # dont update the position
                self.rect.center = self.pos
                return
        
        # check if the proposed position collides with closed doors
        door = pygame.sprite.spritecollideany(self, doors)
        if door:
            if door.toggle:
                # dont update the position
                self.rect.center = self.pos
                self.health.hp -= 0.1
                return
        self.pos = new_pos

        self.health.x = self.pos[0] - 30
        self.health.y = self.pos[1] - 50

        current_time = pygame.time.get_ticks()
        if(current_time - self.last_update >= self.spritesheet.cooldown(self.action)):
            #if animation cooldown has passed between last update and current time, switch frame
            self.current_frame += 1
            self.last_update = current_time
            #reset frame back to 0 so it doesn't index out of bounds
            if(self.current_frame >= self.spritesheet.num_frames(self.action)):
                self.current_frame = 0
            self.image = self.spritesheet.get_image(self.action, self.current_frame)

    def draw(self, surface):
        self.health.draw(surface)
        surface.blit(
            pygame.transform.flip(self.image, self.face_left, False),
            self.rect
        )

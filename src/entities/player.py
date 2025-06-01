import pygame
from src.core.spritesheet import SpriteSheet
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.config as config
import src.constants as c
import src.entities.objects as o
        

class Player(pygame.sprite.Sprite):
    """Represents the player."""

    def __init__(self, filename, pos, stats):
        """Constructor.

            filename: location of png image of the player spritesheet
            pos: tuple representing players inital position
            stats: the player's stats
        """
        super().__init__()
        self.health = o.PlayerHealthBar(pos[0], pos[1], 60, 10, 100)
        self.stamina = o.StaminaBar(pos[0], pos[1], 20, 5, 3)
        self.speed = 4
        self.pos = pygame.Vector2(pos)
        self.spritesheet = SpriteSheet(filename, c.PLAYER_SHEET_METADATA)

        # Animation variables
        self.last_update = pygame.time.get_ticks()
        self.current_frame = 0
        self.action = "idle"
        self.face_left = False

        # Dash variables
        self.last_dash = pygame.time.get_ticks()
        self.dash_time = 100
        self.dash_cooldown = 1500
        self.dash = False

        self.image = self.spritesheet.get_image(self.action, self.current_frame)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.stats = stats

        # Walking sounds
        # self.footstepLeftSound = pygame.mixer.Sound(config.SOUND_DIR / "Footstep_Left_Stone.ogg")
        # self.footstepRightSound = pygame.mixer.Sound(config.SOUND_DIR / "Footstep_Right_Stone.ogg")
        # self.lastFootStepFrame = self.current_frame
    
    def update(self, walls: list[pygame.Rect], doors: pygame.sprite.Group):
        """Updates the player's position."""
        new_pos = pygame.Vector2(self.pos)
        moved = False

        if not self.dash and self.stamina.stamina == 0:   
            self.speed = 1.5
        elif not self.dash:
            self.speed = 5
        else:
            self.speed = 15

        keys = pygame.key.get_pressed()
        self.action = "idle"
        if keys[pygame.K_w]:
            new_pos.y = self.pos.y - self.speed
            moved = True
            self.action = "run"
        if keys[pygame.K_a]:
            new_pos.x = self.pos.x - self.speed
            moved = True
            self.action = "run"
            self.face_left = True
        if keys[pygame.K_s]:
            new_pos.y = self.pos.y + self.speed
            moved = True
            self.action = "run"
        if keys[pygame.K_d]:
            new_pos.x = self.pos.x + self.speed
            moved = True
            self.action = "run"
            self.face_left = False
        if keys[pygame.K_p]:
            self.action = "punch"
        
        if moved:
            EventManager.emit(EcodeEvent.PLAYER_MOVED, target=self.rect)

        if pygame.key.get_just_pressed()[pygame.K_SPACE] and not self.dash and self.stamina.stamina > 0:
            self.last_dash = pygame.time.get_ticks()
            self.dash = True
            self.stamina.stamina -= 1

        
        # tentatively update to the new position
        # might have to undo if it turns out new position
        # collides with a barrier
        self.rect.center = new_pos
        old_pos = self.pos
        self.pos = new_pos

        # check if the proposed position collides with walls
        for wall in walls:
            if pygame.Rect.colliderect(wall, self.rect):
                # dont update the position
                self.rect.center = old_pos
                self.pos = old_pos
        
        # check if the proposed position collides with closed doors
        door = pygame.sprite.spritecollideany(self, doors)
        if door:
            if door.toggle:
                # dont update the position
                self.rect.center = old_pos
                self.pos = old_pos
                self.health.lose(0.1)

        self.health.update(self.pos[0] - 30, self.pos[1] - 50)
        self.stamina.update(self.pos[0] - 30, self.pos[1] - 40)

        current_time = pygame.time.get_ticks()
        
        if self.dash and \
            (current_time - self.last_dash >= self.dash_time):
            self.dash = False
        
        if current_time - self.last_dash >= self.dash_time + self.dash_cooldown:
            if self.stamina.stamina < self.stamina.max_stamina:
                self.stamina.stamina += 1

        if(current_time - self.last_update >= self.spritesheet.cooldown(self.action)):
            self.current_frame += 1
            self.last_update = current_time
            if(self.current_frame >= self.spritesheet.num_frames(self.action)):
                self.current_frame = 0
            self.image = self.spritesheet.get_image(self.action, self.current_frame)
        
        if self.action == "run" and self.current_frame != self.lastFootStepFrame:
            # if self.current_frame == 2:
            #     self.footstepLeftSound.play()
            # elif self.current_frame == 5:
            #     self.footstepRightSound.play()
            self.lastFootStepFrame = self.current_frame

        # if self.health.hp <= 0:
        #     EventManager.emit(EcodeEvent.PLAYER_DIED)

    def draw(self, surface, offset):
        self.health.draw(surface, offset)
        self.stamina.draw(surface, offset)
        surface.blit(
            pygame.transform.flip(self.image, self.face_left, False),
            self.rect.topleft + offset
        )

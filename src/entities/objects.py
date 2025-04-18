"""Classes for different objects within the game."""

import pygame
import time
import random
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.core.utils as utils
import src.constants as c

class StaminaBar():
    """Represents a stamina bar."""
    def __init__(self, x, y, w, h, max_stamina):
        self.x = x 
        self.y = y
        self.w = w 
        self.h = h
        self.stamina = max_stamina
        self.max_stamina = max_stamina
    
    def update(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface, offset):
        for bar in range(self.stamina):
            pygame.draw.rect(surface, "blue",
                             pygame.Rect(self.x + self.w * bar + 1, self.y, self.w - 2, self.h)
                                .move(offset.x, offset.y))
        for bar in range(self.stamina, self.max_stamina):
            pygame.draw.rect(surface, "grey",
                             pygame.Rect(self.x + self.w * bar + 1, self.y, self.w - 2, self.h)
                                .move(offset.x, offset.y))


class HealthBar():
    """Represents a healthbar."""
    def __init__(self, x, y, w, h, max_hp):
        self.x = x 
        self.y = y
        self.w = w 
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp
    
    def update(self, x, y):
        self.x = x
        self.y = y

    def draw(self, surface, offset):
        ratio = self.hp/self.max_hp
        pygame.draw.rect(surface, "red", pygame.Rect(self.x, self.y, self.w, self.h).move(offset.x, offset.y))
        pygame.draw.rect(surface, "green", pygame.Rect(self.x, self.y, self.w * ratio, self.h).move(offset.x, offset.y))
    
    def lose(self, hp):
        self.hp -= hp


class PlayerHealthBar(HealthBar):
    """Represents the player's health bar."""
    def __init__(self, x, y, w, h, max_hp):
        super().__init__(x, y, w, h, max_hp)

class EnemyHealthBar(HealthBar):
    """Represents the enemy's health bar."""
    def __init__(self, x, y, w, h, max_hp):
        super().__init__(x, y, w, h, max_hp)
        self.last_shown = None
        self.cooldown = 2000
    
    def lose(self, hp):
        super().lose(hp)
        self.last_shown = pygame.time.get_ticks()
    
    def draw(self, surface, offset):
        if self.last_shown and pygame.time.get_ticks() - self.last_shown < self.cooldown:
            super().draw(surface, offset)

class Door(pygame.sprite.Sprite):
    """Class to represent doors in the game."""
    
    def __init__(self, rect):
        """Constructor.
        
            rect: pygame.Rect representing the door's area and position
        """
        super().__init__()
        self.rect = rect
        self.scaled_rect = rect.inflate(50, 50)
        self.open_button = ("M", pygame.K_m)
        self.font = pygame.font.Font(size=50)
        self.text = self.font.render(self.open_button[0], True, (250, 250, 250))
        self.textRect = self.text.get_rect()
        self.textRect.left = self.rect.left - self.textRect.width - 20
        self.textRect.top = self.rect.top
        self.bg_rect = self.textRect.inflate(10, 10)
        self.toggle = True
        self.present_button = False
    
    def door_action(self):
        """Runs the action specific to the door.
        
        Default is to turn self.toggle to False.
        """
        self.toggle = False

    def draw_door(self, surface, offset):
        """Logic to draw the door image.
        
        Default is to not draw the door if toggle is False.
        """
        if self.toggle:
            pygame.draw.rect(surface, (252, 3, 3), self.rect.move(offset.x, offset.y))
    
    def handle_event(self, event: pygame.Event):
        """Handle an event off the event queue."""
        if event.type == pygame.KEYDOWN:
            if self.present_button and event.key == self.open_button[1]:
                self.door_action()
    
    def update(self, player):
        """Updates the door based on player position.

        If the player is within the door's range, show the key needed to
        open the door.
            
            player: Player object.
        """
        if self.scaled_rect.colliderect(player.rect) and self.toggle:
            self.present_button = True
        else:
            self.present_button = False
    
    def draw(self, surface, offset):
        """Draw the door to the surface."""
        if self.present_button:
            pygame.draw.rect(surface, (240, 0, 0), self.bg_rect.move(offset.x, offset.y), border_radius=5)
            surface.blit(self.text, self.textRect.topleft + offset)
        self.draw_door(surface, offset)

class LaserDoor(Door):
    """Class to represent a laser door."""

    def __init__(self, rect):
        """Constructor.

            rect: pygame.Rect representing the door's area and position.
        """
        super().__init__(rect)
        
        self.receding = False
        self.last_recede = pygame.time.get_ticks()
        self.recede_cooldown = 200
        self.triedDoor = False

        # Question prompting
        self.speech_bubble = SpeechBubble(
            "",
            pygame.font.Font(size=30),
            (255, 0, 0),
            (0, 0, 0),
            rect.midtop
        )
        
        # Lasers
        self.lasers = []
        self.inner_lasers = []
        laser_width = 4
        inner_laser_width = 2
        num_lasers = 10
        air_gap = (rect.width - laser_width) // (num_lasers - 1) - laser_width
        inner_laser_x_offset = (laser_width - inner_laser_width) / 2
        self.laser_and_air_width = laser_width + air_gap
        
        # Add the laser at the left edge and all lasers in middle
        for i in range(num_lasers - 1):
            left_pos = self.rect.left + i * (laser_width + air_gap)
            self.lasers.append(
                pygame.Rect(
                    left_pos,
                    self.rect.top,
                    laser_width,
                    self.rect.height
                )
            )
            self.inner_lasers.append(
                pygame.rect.Rect(
                    left_pos + inner_laser_x_offset,
                    self.rect.top,
                    inner_laser_width,
                    self.rect.height
                )
            )
        
        # Add the laser that is flush with right edge of door
        end_laser_left_pos = self.rect.right - laser_width
        self.lasers.append(
            pygame.Rect(
                end_laser_left_pos,
                self.rect.top,
                laser_width,
                self.rect.height
            )
        )
        self.inner_lasers.append(
            pygame.Rect(
                end_laser_left_pos + inner_laser_x_offset,
                self.rect.top,
                inner_laser_width,
                self.rect.height
            )
        )

        # Problems associated with this door
        self.problems = pygame.sprite.Group()
    
    def update_receding_animation(self):
        if pygame.time.get_ticks() - self.last_recede > self.recede_cooldown:
            if len(self.lasers) > 1:
                self.lasers = self.lasers[1:]
                self.inner_lasers = self.inner_lasers[1:]
                self.rect.width -= self.laser_and_air_width
                self.rect.left = self.lasers[0].left
                self.last_recede = pygame.time.get_ticks()
            else:
                self.receding = False
                self.toggle = False

    def update(self, player):
        super().update(player)
        if not self.scaled_rect.colliderect(player.rect):
            self.speech_bubble.toggle = False
        
        if self.receding:
            self.update_receding_animation()
    
    def door_action(self):
        if len(self.problems) == 0:
            self.receding = True
        self.speech_bubble.toggle = True

    def handle_event(self, event):
        if (
            event.type == pygame.KEYDOWN
            and self.present_button
            and event.key == self.open_button[1]
        ):
            self.triedDoor = True
            if len(self.problems) > 0:
                pygame.event.post(pygame.Event(c.CHECK_PROBLEMS))
                self.speech_bubble.update_text(
                    f"Trying to open door",
                    (0, 0, 255)
                )
            else:
                self.speech_bubble.update_text(
                    "Door is fully operational",
                    (0, 255, 0)
                )
        elif event.type == c.CHECKED_PROBLEMS and self.triedDoor:
            self.triedDoor = False
            num_problems = len(self.problems)
            if num_problems > 0:
                computer_plural = "computer" if num_problems == 1 else "computers"
                self.speech_bubble.update_text(
                    f"Error: {num_problems} {computer_plural} still broken",
                    (255, 0, 0)
                )
            else:
                self.speech_bubble.update_text(
                    "Door is fully operational",
                    (0, 255, 0)
                )
                self.receding = True
        super().handle_event(event)

    def draw_door(self, surface, offset):
        if self.toggle:
            for i in range(len(self.lasers)):
                pygame.draw.rect(surface, (200, 0, 0), self.lasers[i].move(offset.x, offset.y))
                pygame.draw.rect(surface, (255, 0, 0), self.inner_lasers[i].move(offset.x, offset.y))

    def draw(self, surface, offset):
        if self.present_button and self.toggle and not self.receding:
            pygame.draw.rect(surface, (240, 0, 0), self.bg_rect.move(offset.x, offset.y), border_radius=5)
            surface.blit(self.text, self.textRect.topleft + offset)
        
        self.draw_door(surface, offset)
        self.speech_bubble.draw(surface, offset)


class ExitDoor(Door):
    """Class to represent door that takes player to next level."""

    def door_action(self):
        pygame.event.post(pygame.Event(c.LEVEL_ENDED))


class SpeechBubble():
    """Class to represent the speech bubble of NPC."""

    def __init__(self, text_input, font, text_color, background_color, pos, url=None):
        """Constructor."""
        self.url = url
        self.font = font
        self.background_color = background_color
        
        self.toggle = False

        self.text_input = text_input
        self.text_color = text_color
        self.text_image = self.font.render(self.text_input, True, text_color, wraplength=c.TILE_SIZE * 5)
        self.text_rect = self.text_image.get_rect()
        self.text_rect.midbottom = (pos[0], pos[1] - 10)
        self.bg_rect = self.text_rect.inflate(10, 10)

        self.mouseover = False

    def update_text(self, text_input, text_color=(255, 255, 255)):
        old_midbottom = self.text_rect.midbottom
        self.text_input = text_input
        self.text_color = text_color
        self.text_image = self.font.render(self.text_input, True, text_color, wraplength=c.TILE_SIZE * 5)
        self.text_rect = self.text_image.get_rect()
        self.text_rect.midbottom = old_midbottom
        self.bg_rect = self.text_rect.inflate(10, 10)

    def update_pos(self, pos):
        """Updates position of the speech bubble."""
        self.text_rect.midbottom = (pos[0], pos[1] - 10)
        self.bg_rect = self.text_rect.inflate(10, 10)

    def handle_event(self, event):
        if self.url and self.mouseover and event.type == pygame.MOUSEBUTTONDOWN:
            timestamp = time.time()
            pygame.event.post(pygame.Event(c.OPEN_PROBLEM, {"url": self.url}))
            print(f"Posted event: OPEN_PROBLEM {self.url}, {timestamp}")
    
    def draw(self, surface, offset):
        """Draws the speech bubble and also checks if it is clicked."""
        if self.toggle:
            pygame.draw.rect(surface, self.background_color, self.bg_rect.move(offset.x, offset.y), border_radius=10)
            surface.blit(self.text_image, self.text_rect.move(offset.x, offset.y))

        if self.toggle:
            mouse_pos = pygame.mouse.get_pos()
            if self.bg_rect.move(offset.x, offset.y).collidepoint(mouse_pos):
                self.mouseover = True
            else:
                self.mouseover = False

class Computer(pygame.sprite.Sprite):
    """Class to represent a computer."""

    def __init__(self, rect, text_input):
        super().__init__()
        self.rect = rect
        self.scaled_rect = rect.inflate(50, 50)
        self.note = SpeechBubble(text_input, pygame.font.Font(size=25), (65, 74, 74), (80,199,199), self.rect.midtop)

        # Open button
        self.open_note_button = ("O", pygame.K_o)
        self.button_font = pygame.font.Font(size=50)
        self.button_text = self.button_font.render(self.open_note_button[0], True, (250, 250, 250))
        self.button_textRect = self.button_text.get_rect()
        self.button_textRect.midbottom = (self.rect.midtop[0], self.rect.midtop[1] - 10)
        self.button_bg_rect = self.button_textRect.inflate(10, 10)

        self.present_button = False
    
    def computer_action(self):
        self.present_button = False
        EventManager.emit(EcodeEvent.OPEN_NOTE, text=self.note.text_input)

    def handle_event(self, event):
        self.note.handle_event(event)

    def update(self, player):
        if self.scaled_rect.colliderect(player.rect):
            keys = pygame.key.get_pressed()
            self.present_button = True
            if (keys[self.open_note_button[1]]):
                self.computer_action()
        else:
            self.present_button = False
            self.note.toggle = False      

    def draw(self, surface, offset):
        if self.note.toggle:
            self.note.draw(surface, offset)
        elif self.present_button:
            pygame.draw.rect(surface, (252, 3, 3), self.button_bg_rect.move(offset.x, offset.y), border_radius=5)
            surface.blit(self.button_text, self.button_textRect.move(offset.x, offset.y))


class ProblemComputer(Computer):
    """Class to represent a computer that hosts a LeetCode problem."""

    def __init__(self, rect, textInput, url):
        super().__init__(rect, textInput)
        self.url = url
    
    def computer_action(self):
        self.present_button = False
        EventManager.emit(EcodeEvent.OPEN_NOTE, text=self.note.text_input, url=self.url)

    def handle_event(self, event: pygame.Event):
        super().handle_event(event)
        if event.type == c.PROBLEM_SOLVED:
            self.kill()


class TechNote(pygame.sprite.Sprite):
    """Class to represent a technical note."""

    def __init__(self, filename, pos):
        super().__init__()
        og_image, _ = utils.load_png(filename)
        self.image = pygame.transform.scale(og_image, (72 * 2, 72 * 2))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.pos = pygame.Vector2(pos)
        self.scaled_rect = self.rect.inflate(50, 50)

        self.open_note = ("M", pygame.K_m)
        self.font = pygame.font.Font(size=30)
        self.button_text = self.font.render(self.open_note[0], True, (250, 250, 250), (0, 0, 0))
        self.button_textRect = self.button_text.get_rect()
        self.button_textRect.center = (self.rect.centerx - 100, self.rect.centery - 100)
        self.present_button = False

        text = "A really brute force way would be to search for all possible pairs of numbers but that would be too slow."
        self.note_text = self.font.render(text, True, (250, 250, 25), (0, 0, 0), 72 * 2)
        self.note_textRect = self.note_text.get_rect()
        self.note_textRect.center = (self.rect.centerx - 100, self.rect.centery - 100)
        self.toggle_note = False
    

    def update(self, player):
        """Updates the note based on player position.

        If the player is within the note's range, show the key needed to
        read the note.
            
            player: Player object.
        """
        if self.scaled_rect.colliderect(player.rect):
            keys = pygame.key.get_pressed()
            self.present_button = True
            if (keys[self.open_note[1]]):
                self.toggle_note = True
        else:
            self.present_button = False
            self.toggle_note = False
    
    def draw(self, surface, offset):
        """Draw the note to the surface."""
        #surface.blit(self.image, self.rect.topleft + offset)
        if self.present_button:
            surface.blit(self.button_text, self.button_textRect.topleft + offset)
        if self.toggle_note:
            surface.blit(self.note_text, self.note_textRect.topleft + offset)

class StaticItem(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, filename=None):
        super().__init__()
        self.pos = pos
        #self.image, self.rect = utils.load_png(filename)
        self.rect = pygame.Rect(self.pos[0], self.pos[1], width * c.TILE_SIZE, height * c.TILE_SIZE)
        self.rect.topleft = self.pos
    
    def draw(self, surface, offset):
        pygame.draw.rect(surface, (219, 134, 111), self.rect.move(offset))
        # surface.blit(self.image, self.rect.topleft + offset)

class DanceFloor(StaticItem):

    DISCO_COLORS = [(255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 0, 255)]

    def __init__(self, pos, width=5, height=5):
        super().__init__(pos, width, height)
        self.rect.width = 448
        self.rect.height = 320
        self.light_pos = []
        self.colors = []
        self.on_dance_floor = False
        self.disco_timer = pygame.time.get_ticks()

    def update(self, player):
        if self.rect.colliderect(player.rect):
            if not self.on_dance_floor:
                pygame.event.post(pygame.event.Event(c.ENTERED_DANCE_FLOOR))
            self.on_dance_floor = True
        else:
            if self.on_dance_floor:
                pygame.event.post(pygame.event.Event(c.LEFT_DANCE_FLOOR))
            self.on_dance_floor = False

        if self.on_dance_floor:
            if pygame.time.get_ticks() - self.disco_timer > 1000:  # Change every second
                self.disco_timer = pygame.time.get_ticks()
                self.light_pos = []
                self.colors = []
                for i in range(10):  # Number of lights
                    x = random.randint(self.rect.left, self.rect.right)
                    y = random.randint(self.rect.top, self.rect.bottom)
                    self.light_pos.append((x, y))
                    self.colors.append(random.choice(DanceFloor.DISCO_COLORS))
        
    def draw(self, surface, offset):
        if self.on_dance_floor:
            for i, pos in enumerate(self.light_pos):
                pygame.draw.circle(surface, self.colors[i], pos + offset, 15)

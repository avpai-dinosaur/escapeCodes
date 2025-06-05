"""Classes for different objects within the game."""

import pygame
import time
import random
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.core.utils as utils
import src.constants as c
from src.components.ui import KeyPromptUi

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
        self.open_button = pygame.K_m
        self.toggle = True
        self.present_button = False
        self.keyPromptUi = KeyPromptUi(self.open_button, "Keys/M-Key.png", c.SM_KEY_SHEET_METADATA)
        self.keyPromptUi.rect.bottom = self.rect.top - 10
        self.keyPromptUi.rect.centerx = self.rect.centerx
    
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
            if self.present_button and event.key == self.open_button:
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
        
        if self.present_button:
            self.keyPromptUi.update()
    
    def draw(self, surface, offset):
        """Draw the door to the surface."""
        if self.present_button:
            self.keyPromptUi.draw(surface, offset)
        self.draw_door(surface, offset)

class LaserDoor(Door):
    """Class to represent a laser door."""

    id = 0
    giveTutorial = True

    def __init__(self, rect, pin):
        """Constructor.

            rect: pygame.Rect representing the door's area and position.
        """
        super().__init__(rect)
        
        self.receding = False
        self.last_recede = pygame.time.get_ticks()
        self.recede_cooldown = 200
        self.triedDoor = False
        self.id = LaserDoor.id
        LaserDoor.id += 1
        self.pin = pin

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

        # Event Subscribers
        EventManager.subscribe(EcodeEvent.OPEN_DOOR, self.on_open_door)

    def on_open_door(self, id):
        if id == self.id:
            self.receding = True
    
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
        if self.pin != 0:
            EventManager.emit(EcodeEvent.OPEN_PIN, pin=self.pin, id=self.id)
            if LaserDoor.giveTutorial:
                EventManager.emit(
                    EcodeEvent.GIVE_ORDER,
                    text="Explore the environment to discover the pin to locked doors."
                )
                LaserDoor.giveTutorial = False
        else:
            self.receding = True

    def draw_door(self, surface, offset):
        if self.toggle:
            for i in range(len(self.lasers)):
                pygame.draw.rect(surface, (200, 0, 0), self.lasers[i].move(offset.x, offset.y))
                pygame.draw.rect(surface, (255, 0, 0), self.inner_lasers[i].move(offset.x, offset.y))

    def draw(self, surface, offset):
        if self.present_button and self.toggle and not self.receding:
            self.keyPromptUi.draw(surface, offset)
        
        self.draw_door(surface, offset)
        self.speech_bubble.draw(surface, offset)


class ExitDoor(Door):
    """Class to represent door that takes player to next level."""

    def door_action(self):
        EventManager.emit(EcodeEvent.LEVEL_ENDED)


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

    def __init__(self, rect, textInput):
        super().__init__()
        self.rect = rect
        self.scaled_rect = rect.inflate(50, 50)
        self.textInput = textInput

        # Open button
        self.open_note_button = pygame.K_m
        self.keyPromptUi = KeyPromptUi(self.open_note_button, "Keys/M-Key.png", c.SM_KEY_SHEET_METADATA)
        self.keyPromptUi.rect.bottom = self.rect.top - 10
        self.keyPromptUi.rect.centerx = self.rect.centerx
        
        self.present_button = False
    
    def computer_action(self):
        self.present_button = False
        EventManager.emit(EcodeEvent.OPEN_NOTE, text=self.textInput)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.open_note_button and self.present_button:
                self.computer_action()

    def update(self, player):
        self.present_button = self.scaled_rect.colliderect(player.rect)
        if self.present_button:
            self.keyPromptUi.update()

    def draw(self, surface, offset):
        if self.present_button:
            self.keyPromptUi.draw(surface, offset)


class ProblemComputer(Computer):
    """Class to represent a computer that hosts a LeetCode problem."""

    def __init__(self, rect, textInput, url, pinText):
        super().__init__(rect, textInput)
        self.url = url
        self.problemSlug = None
        self.isSolved = False
        self.pinText = pinText
        # TODO: Remove this
        if self.url != "https://www.google.com/":
            self.problemSlug = utils.get_problem_slug(url)

        # Event subscribers
        EventManager.subscribe(EcodeEvent.PROBLEM_SOLVED, self.on_problem_solved)
    
    def on_problem_solved(self, problemSlug : str):
        if problemSlug == self.problemSlug:
            self.isSolved = True
            self.open_note()

    def computer_action(self):
        self.present_button = False
        if not self.isSolved:
            EventManager.emit(EcodeEvent.CHECK_PROBLEMS)
        self.open_note()
    
    def open_note(self):
        EventManager.emit(
            EcodeEvent.OPEN_NOTE,
            text=self.textInput,
            url=self.url,
            isSolved=self.isSolved,
            pinText=self.pinText
        )


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

import pygame
from random import randint
from enum import Enum
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.core.level import Level
import src.constants as c

class Tutorial(Level):
    def __init__(self):
        super().__init__("level0.png", "level0.tmj")

class Level1(Level):
    def __init__(self, imageFile, dataFile):
        super().__init__(imageFile, dataFile)

    def load_entities(self):
        super().load_entities()
        self.boss = Boss(pygame.Vector2(2560, 256))
    
    def load_camera(self, camera):
        super().load_camera(camera)
        camera.add(self.boss)
    
    def handle_event(self, event):
        super().handle_event(event)
        self.boss.handle_event(event)

    def update(self):
        super().update()
        if self.boss.rect.colliderect(self.player.rect):
            if self.boss.state == Boss.BossState.ATTACK:
                self.player.health.lose(1)
            elif self.boss.state == Boss.BossState.DISABLE and self.player.action == "punch":
                if self.boss.health > 0:
                    self.boss.health -= 1
        if (
            self.boss.rect.inflate(50, 50).colliderect(self.player.rect)
            and self.boss.state == Boss.BossState.ATTACK
        ):
            EventManager.emit(EcodeEvent.OPEN_BAR)
        if self.boss.roomRect.colliderect(self.player.rect) and self.boss.state == Boss.BossState.WAITING:
            EventManager.emit(EcodeEvent.START_BOSS_FIGHT)
        self.boss.update()
    

class Boss(pygame.sprite.Sprite):
    """Class to represent entity that player fights to complete a level."""

    class BossState(Enum):
        WAITING = 0
        ATTACK = 1
        DISABLE = 2
        DEAD = 3

    def __init__(self, pos: pygame.Vector2):
        super().__init__()
        self.pos = pos
        self.rect = pygame.Rect(pos.x, pos.y, 64 * 3, 64 * 3)
        self.health = 100
        self.roomRect = pygame.Rect(
            39 * c.TILE_SIZE,
            2 * c.TILE_SIZE,
            11 * c.TILE_SIZE,
            17 * c.TILE_SIZE
        )
        self.speed = 10
        self.color = "grey"
        self.disableStart = pygame.time.get_ticks()
        self.get_next_pos()

        # State Management
        self.finiteStateMachine = {
            (Boss.BossState.WAITING, EcodeEvent.START_BOSS_FIGHT): self.start_fight,
            (Boss.BossState.ATTACK, EcodeEvent.HIT_BAR): self.disable
        } # Maps (state, incoming_event) -> transition function
        self.updateBehaviors = {
            Boss.BossState.WAITING: lambda : None,
            Boss.BossState.ATTACK: self.update_attack,
            Boss.BossState.DISABLE: self.update_disable
        } # Maps state -> update function
        self.state = Boss.BossState.WAITING
        for _, ecodeEvent in self.finiteStateMachine:
            EventManager.subscribe(ecodeEvent, self.build_ecode_event_handler(ecodeEvent))

    def build_ecode_event_handler(self, event: EcodeEvent):
        def event_handler():
            if (self.state, event) in self.finiteStateMachine:
                self.finiteStateMachine[(self.state, event)]()
        return event_handler
    
    def add_transition(self, state: BossState, event, func):
        """Add a transition to finite state machine of boss."""
        if (state, event) in self.finiteStateMachine.keys():
            raise RuntimeError(
                f"Transition already exists for state '{state}' and event '{event}'"
            )
        else:
            self.finiteStateMachine[(state, event)] = func

    def get_next_pos(self):
        x = randint(39, 49 - 3)
        y = randint(3, 18 - 3)
        self.nextPos = pygame.Vector2(x * c.TILE_SIZE, y * c.TILE_SIZE)

    def start_fight(self):
        EventManager.emit(EcodeEvent.GET_PROBLEM_DESCRIPTION, url="https://leetcode.com/problems/two-sum/description/")
        self.state = Boss.BossState.ATTACK
        self.color = "red"

    def disable(self):
        self.state = Boss.BossState.DISABLE
        self.disableStart = pygame.time.get_ticks()
        self.color = "grey"

    def update_attack(self):
        if self.move(self.nextPos):
            self.get_next_pos()
        
    def update_disable(self):
        if pygame.time.get_ticks() - self.disableStart > 3000:
            self.state = Boss.BossState.ATTACK
            self.color = "red"

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
    
    def handle_event(self, event: pygame.Event):
        if event.type == c.PROBLEM_DESCRIPTION:
            print(event.slug, event.description)

    def update(self):
        if self.health == 0:
            self.state = Boss.BossState.DEAD
        if self.state != Boss.BossState.DEAD:
            self.updateBehaviors[self.state]()

    def draw(self, surface, offset):
        if self.state != Boss.BossState.DEAD:
            healthRect = pygame.Rect(0, 0, self.rect.width, self.rect.height * (self.health / 100))
            healthRect.bottomleft = self.rect.bottomleft
            pygame.draw.rect(surface, self.color, self.rect.move(offset[0], offset[1]), border_radius=10)
            if self.state == Boss.BossState.DISABLE:
                pygame.draw.rect(surface, "green", healthRect.move(offset[0], offset[1]), border_radius=10)

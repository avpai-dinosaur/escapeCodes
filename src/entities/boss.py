"""
boss.py
Boss that the player has to fight at end of level.
"""

import pygame
from enum import Enum
from random import randint
from src import constants as c
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.entities.player import Player

class FiniteStateMachine():
    """Class to represent a simple finite state machine."""
    
    def __init__(self):
        """Constructor."""
        self.fsm = {}
        self.updates = {}
        self.enters = {}
        self.state = None
    
    def check_state(self, state):
        """Check if a state exists in the fsm.
        
            state: The state to check
        """
        if state not in self.updates:
            raise RuntimeError(
                f"Finite state machine does not contain state {state}"
            )

    def set_state(self, newState):
        """Set the state of the fsm.
        
            newState: The new state
        """
        self.enters[newState]()
        self.state = newState

    def add_state(self, state, update_func, enter_func=lambda: None):
        """Add a state to the fsm.
        
            state: The state to add
            update_func: The function to run every tick when the given state becomes current
            enter_func: Optional function to execute once upon entering the given state
        """
        if state in self.updates:
            raise RuntimeError(
                f"State {state} already exists with update function {self.updates[state]}"
            )
        self.updates[state] = update_func
        self.enters[state] = enter_func
        return self

    def add_transition(self, state, nextState, ecodeEvent: EcodeEvent, transition_func=lambda: None):
        """Add a transition to the fsm.

            state: The source state of this transition
            nextState: The target state of this trantision
            ecodeEvent: The event upon which to trigger the transition
            transition_func: Optional function to execute before transitioning
        """
        if (state, ecodeEvent) in self.fsm:
            raise RuntimeError(
                f"Transition already exists for state '{state}' and event '{ecodeEvent}'"
            )
        self.check_state(state)
        self.check_state(nextState)
        
        def wrapped_func():
            transition_func()
            self.set_state(nextState)
           
        self.fsm[(state, ecodeEvent)] = wrapped_func
        return self

    def build_subscriber(self, state, event: EcodeEvent):
        """Build subscriber for a state transition.
        
            state: The source state
            event: The event to trigger the transition
        """
        def subscriber():
            if self.state == state:
                self.fsm[(state, event)]()
        return subscriber
    
    def build(self, initialState):
        """Build the fsm.
        
            initialState: 
        """
        self.check_state(initialState)
        self.state = initialState
        for state, ecodeEvent in self.fsm:
            EventManager.subscribe(ecodeEvent, self.build_subscriber(state, ecodeEvent))
        return self
    
    def update(self, *args):
        self.updates[self.state](*args)


class Boss(pygame.sprite.Sprite):
    """Class to represent entity that player fights to complete a level."""

    class BossState(Enum):
        WAITING = 0
        CHARGE = 1
        ATTACK = 2
        DYING = 3

    def __init__(
        self,
        pos: pygame.Vector2,
        room: pygame.Rect,
        problemSlug: str
    ):
        """Constructor.

            pos: Initial position of boss
            room: Boundaries of when boss fight is activated
            problemSlug: Url slug of problem this boss is associated with
        """
        super().__init__()
        self.pos = pos
        self.rect = pygame.Rect(pos.x, pos.y, 64 * 3, 64 * 3)
        self.room = room
        self.problemSlug = problemSlug
        self.fsm = FiniteStateMachine()
        self.health = 100
        self.speed = 10
        self.color = "grey"

        # Attacking data
        self.nextPos = self.get_next_pos()

        # Timers
        self.chargeStart = pygame.time.get_ticks()
        self.dyingStart = pygame.time.get_ticks()
        self.attackStart = pygame.time.get_ticks()

        # State Machine
        (
            self.fsm
                .add_state(Boss.BossState.WAITING, self.waiting_update, lambda : print("waiting state"))
                .add_state(Boss.BossState.CHARGE, self.charge_update, self.charge_enter)
                .add_state(Boss.BossState.ATTACK, self.attack_update, self.attack_enter)
                .add_state(Boss.BossState.DYING, self.dying_update, self.dying_enter)
                .add_transition(Boss.BossState.CHARGE, Boss.BossState.DYING, EcodeEvent.FOUND_BUG)
                .build(Boss.BossState.WAITING)
        )

        # Event Subscriber
        EventManager.subscribe(EcodeEvent.HIT_BAR, self.hack)

    def charge_enter(self):
        self.chargeStart = pygame.time.get_ticks()
        self.color = "blue"
        EventManager.emit(EcodeEvent.BOSS_CHARGE)

    def attack_enter(self):
        self.attackStart = pygame.time.get_ticks()
        self.color = "orange"
        EventManager.emit(EcodeEvent.BOSS_ATTACK)

    def dying_enter(self):
        self.dyingStart = pygame.time.get_ticks()
        self.color = "red"

    def waiting_update(self, player: Player):
        if self.room.colliderect(player.rect):
            self.fsm.set_state(Boss.BossState.CHARGE)

    def charge_update(self, _):
        if pygame.time.get_ticks() - self.chargeStart > 10000:
            self.fsm.set_state(Boss.BossState.ATTACK)

    def attack_update(self, player: Player):
        if self.rect.colliderect(player.rect):
            player.health.lose(1)
        if pygame.time.get_ticks() - self.attackStart > 10000:
            self.fsm.set_state(Boss.BossState.CHARGE)
        if self.move(self.nextPos):
            self.nextPos = self.get_next_pos()

    def dying_update(self, _):
        if pygame.time.get_ticks() - self.dyingStart > 3000:
            self.fsm.set_state(Boss.BossState.WAITING)

    def hack(self):
        EventManager.emit(EcodeEvent.BOSS_HACK, problemSlug=self.problemSlug)

    def get_next_pos(self):
        x = randint(39, 49 - 3)
        y = randint(3, 18 - 3)
        return pygame.Vector2(x * c.TILE_SIZE, y * c.TILE_SIZE)

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

    def update(self, player: Player):
        self.fsm.update(player)

    def draw(self, surface, offset):
        pygame.draw.rect(surface, self.color, self.rect.move(offset[0], offset[1]), border_radius=10)
        # if self.state != Boss.BossState.DEAD:
        #     healthRect = pygame.Rect(0, 0, self.rect.width, self.rect.height * (self.health / 100))
        #     healthRect.bottomleft = self.rect.bottomleft
        #     pygame.draw.rect(surface, self.color, self.rect.move(offset[0], offset[1]), border_radius=10)
        #     if self.state == Boss.BossState.DISABLE:
        #         pygame.draw.rect(surface, "green", healthRect.move(offset[0], offset[1]), border_radius=10)
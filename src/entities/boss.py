"""
boss.py
Boss that the player has to fight at end of level.
"""

import pygame
from enum import Enum
from random import randint
from src import constants as c
from src.components.ui import KeyPromptUi
from src.core.spritesheet import SpriteSheet
from src.core.ecodeEvents import EventManager, EcodeEvent
from src.entities.player import Player

class FiniteStateMachine():
    """Class to represent a simple finite state machine."""
    
    def __init__(self):
        """Constructor."""
        self.fsm = {}
        self.updates = {}
        self.eventHandlers = {}
        self.enters = {}
        self.subscribers = []
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

    def add_state(self, state, update_func, handle_event_func, enter_func=lambda: None):
        """Add a state to the fsm.
        
            state: The state to add
            update_func: The function to run every tick when the given state becomes current
            handle_event_func: The function to run to get events off the event queue
                when the given state becomes current
            enter_func: Optional function to execute once upon entering the given state
        """
        if state in self.updates:
            raise RuntimeError(
                f"State {state} already exists with update function {self.updates[state]}"
            )
        self.updates[state] = update_func
        self.eventHandlers[state] = handle_event_func
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
            sub = self.build_subscriber(state, ecodeEvent)
            self.subscribers.append((ecodeEvent, sub))
            EventManager.subscribe(ecodeEvent, sub)
        return self
    
    def destroy(self):
        """Clean up all the subscribers created by the fsm."""
        for ecodeEvent, sub in self.subscribers:
            EventManager.unsubscribe(ecodeEvent, sub)

    def handle_event(self, event: pygame.Event):
        self.eventHandlers[self.state](event)

    def update(self, *args):
        self.updates[self.state](*args)


class Boss(pygame.sprite.Sprite):
    """Class to represent entity that player fights to complete a level."""

    class BossState(Enum):
        WAITING = 0
        START_DIALOG = 1
        CHARGE = 2
        ATTACK = 3
        DYING = 4
        DEATH_DIALOG = 5

    def __init__(
        self,
        room: pygame.Rect,
        problemSlug: str
    ):
        """Constructor.

            pos: Initial position of boss
            room: Boundaries of when boss fight is activated
            problemSlug: Url slug of problem this boss is associated with
        """
        super().__init__()
        self.room = room
        self.pos = pygame.Vector2(
            self.room.left + self.room.width / 2,
            self.room.top + self.room.height / 2
        )
        self.problemSlug = problemSlug
        self.fsm = FiniteStateMachine()
        self.speed = 10

        # Animation variables
        self.spritesheet = SpriteSheet("druck.png", c.DRUCK_SHEET_METADATA)
        self.action = "charge"
        self.currentFrame = 0
        self.lastUpdate = pygame.time.get_ticks()

        # Image variables
        self.image = self.spritesheet.get_image(self.action, self.currentFrame)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.showKeyPrompt = False
        self.keyPromptUi = KeyPromptUi(pygame.K_t, "Keys/T-Key.png")
        self.keyPromptUi.rect.bottom = self.rect.top - 10
        self.keyPromptUi.rect.centerx = self.rect.centerx

        # Attacking data
        self.nextPos = self.get_next_pos()
        self.attackedOnce = False

        # Timers
        self.chargeStart = pygame.time.get_ticks()
        self.dyingStart = pygame.time.get_ticks()
        self.attackStart = pygame.time.get_ticks()

        # State Machine
        (
            self.fsm
                .add_state(Boss.BossState.WAITING, self.waiting_update, self.waiting_handle_event)
                .add_state(Boss.BossState.START_DIALOG, self.start_dialog_update, self.start_dialog_handle_event, self.start_dialog_enter)
                .add_state(Boss.BossState.CHARGE, self.charge_update, self.charge_handle_event, self.charge_enter)
                .add_state(Boss.BossState.ATTACK, self.attack_update, self.attack_handle_event, self.attack_enter)
                .add_state(Boss.BossState.DYING, self.dying_update, self.dying_handle_event, self.dying_enter)
                .add_state(Boss.BossState.DEATH_DIALOG, self.death_dialog_update, self.death_dialog_handle_event)
                .add_transition(Boss.BossState.START_DIALOG, Boss.BossState.CHARGE, EcodeEvent.FINISHED_DIALOG)
                .add_transition(Boss.BossState.CHARGE, Boss.BossState.DYING, EcodeEvent.KILL_BOSS)
                .build(Boss.BossState.WAITING)
        )

        # Event Subscriber
        EventManager.subscribe(EcodeEvent.HIT_BAR, self.hack)

    def start_dialog_enter(self):
        """Execute once upon entering dialog state."""
        EventManager.emit(EcodeEvent.OPEN_DIALOG, lines=["TODO: Set boss dialog"], currentLine=0)

    def charge_enter(self):
        """Execute once upon entering charge state."""
        self.chargeStart = pygame.time.get_ticks()
        self.action = "charge"
        self.currentFrame = 0
        if self.attackedOnce:
            # Allow one attack cycle to occur before player can hack
            EventManager.emit(EcodeEvent.BOSS_CHARGE)

    def attack_enter(self):
        """Execute once upon entering attack state."""
        self.attackStart = pygame.time.get_ticks()
        self.action = "attack"
        self.currentFrame = 0
        self.attackedOnce = True
        EventManager.emit(EcodeEvent.BOSS_ATTACK)

    def dying_enter(self):
        """Execute once upon entering dying state."""
        self.dyingStart = pygame.time.get_ticks()
        self.action = "dying"
        self.currentFrame = 0

    def waiting_update(self, player: Player):
        """Update function to run when in waiting state."""
        self.showKeyPrompt = self.rect.inflate(50, 50).colliderect(player.rect)
        if self.room.left + c.TILE_SIZE < player.rect.left:
            EventManager.emit(EcodeEvent.CLOSE_DOORS)
        
    def start_dialog_update(self, _):
        """Update function to run when in start dialog state."""
        pass

    def charge_update(self, _):
        """Update function to run when in charge state."""
        if pygame.time.get_ticks() - self.chargeStart > 3000:
            self.fsm.set_state(Boss.BossState.ATTACK)

    def attack_update(self, player: Player):
        """Update function to run when in attack state."""
        if self.rect.colliderect(player.rect):
            player.health.lose(1)
        if pygame.time.get_ticks() - self.attackStart > 3000:
            self.fsm.set_state(Boss.BossState.CHARGE)
        if self.move(self.nextPos):
            self.nextPos = self.get_next_pos()

    def dying_update(self, _):
        """Update function to run when in dying state."""
        if pygame.time.get_ticks() - self.dyingStart > 3000:
            self.destroy()
    
    def death_dialog_update(self, _):
        """Update function to run when in death dialog state."""
        pass

    def waiting_handle_event(self, event: pygame.Event):
        """Event handler to run when in waiting state."""
        if event.type == pygame.KEYDOWN:
            if event.key == self.keyPromptUi.key and self.showKeyPrompt:
                self.fsm.set_state(Boss.BossState.START_DIALOG)
                self.showKeyPrompt = False

    def start_dialog_handle_event(self, event: pygame.Event):
        """Event handler to run when in the start dialog state."""
        pass

    def charge_handle_event(self, event: pygame.Event):
        """Event handler to run when in charge state."""
        pass

    def attack_handle_event(self, event: pygame.Event):
        """Event handler to run when in attack state."""
        pass

    def dying_handle_event(self, event: pygame.Event):
        """Event handler to run when in dying state."""
        pass

    def death_dialog_handle_event(self, event: pygame.Event):
        """Event handler to run when in death dialog state."""
        pass

    def hack(self):
        """Trigger an attempt to hack the boss."""
        EventManager.emit(EcodeEvent.BOSS_HACK, problemSlug=self.problemSlug)

    def get_next_pos(self):
        x = randint(self.room.left, self.room.right)
        y = randint(self.room.top, self.room.bottom)
        return pygame.Vector2(x, y)

    def move(self, target: pygame.Vector2):
        """Move boss to the target point.

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

    def destroy(self):
        """Clean up references to boss."""
        EventManager.unsubscribe(EcodeEvent.HIT_BAR, self.hack)
        self.fsm.destroy()
        self.kill()

    def update_animation(self):
        """Update animation of boss."""
        currentTime = pygame.time.get_ticks()
        if(currentTime - self.lastUpdate >= self.spritesheet.cooldown(self.action)):
            self.currentFrame += 1
            self.lastUpdate = currentTime
            if(self.currentFrame >= self.spritesheet.num_frames(self.action)):
                self.currentFrame = 0
            self.image = self.spritesheet.get_image(self.action, self.currentFrame)

    def handle_event(self, event: pygame.Event):
        self.fsm.handle_event(event)

    def update(self, player: Player):
        self.fsm.update(player)
        self.update_animation()

    def draw(self, surface: pygame.Surface, offset):
        if self.showKeyPrompt:
            self.keyPromptUi.draw(surface, offset)
        surface.blit(self.image, self.rect.move(offset[0], offset[1]))


class Druck(Boss):
    """Class representing boss player encounters at end of level 3."""

    def start_dialog_enter(self):
        EventManager.emit(
            EcodeEvent.OPEN_DIALOG,
            lines=[
"""i told them...
i told them they'd need me for what comes next...
i dedicated more of our energy to this than any of the other companies in the galaxy...""",
"""this was our roadmap to the future...
seven years of preparation...and this is how I'm rewarded?""",
"""HEY! WHA...?! WHO ARE YOU!""",
"""a spy...it must be...but it looks so weak""",
"""perhaps this presents an opportunity to test my modifications...""",
"""Underling, you must enjoy technology? Of course you do, how could you not!
Would you like to see a demonstration of my latest product?
Just stand still. I'll make this quick."""
            ],
            currentLine=0
        )
        self.showKeyPrompt = False

    def dying_enter(self):
        EventManager.emit(
            EcodeEvent.OPEN_DIALOG,
            lines=["""I am overruling you! I am overruling..."""],
            currentLine=0
        )
        super().dying_enter()

    def attack_update(self, player: Player):
        """Update function to run when in attack state."""
        if self.rect.colliderect(player.rect):
            player.health.lose(1)
        if pygame.time.get_ticks() - self.attackStart > 3000:
            self.fsm.set_state(Boss.BossState.CHARGE)
        if self.move(self.nextPos):
            if self.room.colliderect(player.rect):
                self.nextPos = player.rect.topleft
            else:
                self.fsm.set_state(Boss.BossState.WAITING)
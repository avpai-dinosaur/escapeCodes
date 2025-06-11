import pygame
from collections import defaultdict, deque
from enum import Enum

class EcodeEvent(Enum):
    PLAYER_MOVED = 1
    LEVEL_ENDED = 2
    ENTERED_DANCE_FLOOR = 3
    LEFT_DANCE_FLOOR = 4
    PLAYER_DIED = 5
    OPEN_PROBLEM = 6
    PROBLEM_SOLVED = 7
    CHECK_PROBLEMS = 8
    CHECKED_PROBLEMS = 9
    USER_LOGIN = 10
    OPEN_NOTE = 11
    CLOSE_NOTE = 12
    OPEN_BAR = 13
    HIT_BAR = 14
    START_BOSS_FIGHT = 15
    GET_PROBLEM_DESCRIPTION = 16
    KILL_BOSS = 18

    # Boss state change events
    BOSS_CHARGE = 19
    BOSS_ATTACK = 20
    BOSS_HACK = 21

    PAUSE_GAME = 22
    UNPAUSE_GAME = 23

    OPEN_DIALOG = 24
    FINISHED_DIALOG = 25

    OPEN_PIN = 26
    OPEN_DOOR = 27

    GIVE_ORDER = 28
    CAMERA_SHAKE = 29
    CAMERA_BLACKOUT = 30
    CAMERA_ALARM = 31

    NEXT_LEVEL = 32

    OPEN_KEY_PROMPT = 33
    OPEN_WASD = 34

    CLOSE_DOORS = 35


class ScheduledEvent:
    def __init__(self, event: EcodeEvent, triggerTime: int, kwargs):
        self.event = event
        self.triggerTime = triggerTime
        self.kwargs = kwargs


class EventManager:
    """Class to represent an event subscription system."""

    listeners = defaultdict(list)
    scheduled = deque()

    def subscribe(event: EcodeEvent, callback):
        """Subscribe to an event.
        
            event: Event to subscribe to
            callback: Subscriber function
        """
        EventManager.listeners[event].append(callback)
    
    def unsubscribe(event: EcodeEvent, callback):
        """Unsubscribe from an event.
        
            event: Event to unsubscribe from
            callback: Function to unsubscribe
        """
        EventManager.listeners[event].remove(callback)

    def emit(event: EcodeEvent, delay: int=0, **kwargs):
        """Emit an event.
        
            event: Event to emit.
            delay: Time in milliseconds to wait before emitting this event
            **kwargs: Keyword arguments to pass to subscriber callbacks.
        """
        if delay == 0:
            for func in EventManager.listeners[event]:
                func(**kwargs)
        else:
            triggerTime = pygame.time.get_ticks() + delay
            EventManager.scheduled.append(ScheduledEvent(event, triggerTime, kwargs))
    
    def update():
        """Emit scheduled events."""
        now = pygame.time.get_ticks()
        while len(EventManager.scheduled) > 0 and EventManager.scheduled[0].triggerTime <= now:
            scheduledEvent = EventManager.scheduled.popleft()
            for func in EventManager.listeners[scheduledEvent.event]:
                func(**scheduledEvent.kwargs) 
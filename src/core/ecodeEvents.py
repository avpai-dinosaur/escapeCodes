import pygame
import weakref
from collections import defaultdict, deque
from enum import Enum
from typing import Callable, Any

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
    PAUSE_MENU = 36
    
    OPEN_DOWNLOAD = 37
    OPEN_PSEUDOCODE = 38


class ScheduledEvent:
    def __init__(self, event: EcodeEvent, triggerTime: int, kwargs):
        self.event = event
        self.triggerTime = triggerTime
        self.kwargs = kwargs


class EventManager:
    """Class to represent an event subscription system."""

    # Maps an event to a list of weak references to callback functions
    listeners = defaultdict(list)
    scheduled = deque()

    @staticmethod
    def _make_weakref(callback: Callable):
        """Return a weak reference to the callback."""
        if hasattr(callback, "__self__") and callback.__self__ is not None:
            return weakref.WeakMethod(callback)
        else:
            return weakref.ref(callback)
    
    @staticmethod
    def _get_bound_identity(callback: Callable):
        """Return (object, function) tuple for a bound method, or (None, function) for free function."""
        if hasattr(callback, "__self__") and callback.__self__ is not None:
            return (callback.__self__, callback.__func__)
        return (None, callback)
    
    @staticmethod
    def _is_same_callback(ref, callback: Callable):
        """Return if the callback is the same as the one referenced by ref."""
        targetObj, targetFunc = EventManager._get_bound_identity(callback)
        func = ref()
        if not func:
            return False
        refObj, refFunc = EventManager._get_bound_identity(func)
        return refObj == targetObj and targetFunc == refFunc 

    @staticmethod
    def subscribe(event: EcodeEvent, callback):
        """Subscribe to an event.
        
            event: Event to subscribe to
            callback: Subscriber function
        """
        ref = EventManager._make_weakref(callback)
        EventManager.listeners[event].append(ref)
    
    @staticmethod
    def unsubscribe(event: EcodeEvent, callback):
        """Unsubscribe from an event.
        
            event: Event to unsubscribe from
            callback: Function to unsubscribe
        """
        EventManager.listeners[event] = [
            ref for ref in EventManager.listeners[event]
            if not EventManager._is_same_callback(ref, callback)
        ]

    @staticmethod
    def emit(event: EcodeEvent, delay: int=0, **kwargs):
        """Emit an event.
        
            event: Event to emit.
            delay: Time in milliseconds to wait before emitting this event
            **kwargs: Keyword arguments to pass to subscriber callbacks.
        """
        if delay == 0:
            newList = []
            for ref in EventManager.listeners[event]:
                func = ref()
                if func:
                    func(**kwargs)
                    newList.append(ref)
            EventManager.listeners[event] = newList # Remove dead references
        else:
            triggerTime = pygame.time.get_ticks() + delay
            EventManager.scheduled.append(ScheduledEvent(event, triggerTime, kwargs))
    
    @staticmethod
    def update():
        """Emit scheduled events."""
        now = pygame.time.get_ticks()
        while len(EventManager.scheduled) > 0 and EventManager.scheduled[0].triggerTime <= now:
            scheduledEvent = EventManager.scheduled.popleft()
            newList = []
            for ref in EventManager.listeners[scheduledEvent.event]:
                func = ref()
                if func:
                    func(**scheduledEvent.kwargs) 
                    newList.append(ref)
            EventManager.listeners[scheduledEvent.event] = newList # Remove dead references
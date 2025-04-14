from collections import defaultdict
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

class EventManager:
    listeners = defaultdict(list)

    def subscribe(event: EcodeEvent, callback):
        EventManager.listeners[event].append(callback)
    
    def emit(event: EcodeEvent, **kwargs):
        for func in EventManager.listeners[event]:
            func(**kwargs)
    
    def unsubscribe(event: EcodeEvent, callback):
        EventManager.listeners[event].remove(callback)
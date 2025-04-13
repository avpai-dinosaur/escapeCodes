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

class EventManager:
    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event: EcodeEvent, callback: function):
        self.listeners[event].append(callback)
    
    def emit(self, event: EcodeEvent, **kwargs):
        for func in self.listeners[event]:
            func(**kwargs)
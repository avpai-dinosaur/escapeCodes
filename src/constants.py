"""Useful constants."""

import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800

MAP_WIDTH = 40
MAP_HEIGHT = 25
TILE_SIZE = 64
INIT_PLAYER_POS = (256, 256)
ENEMY_SPEED = 1.5
ENEMY_CHASE_SPEED = 0.7

WALKABLE_TILES = [12, 31, 32, 33]

# Custom events
LEVEL_ENDED = pygame.USEREVENT + 2
ENTERED_DANCE_FLOOR = pygame.USEREVENT + 3
LEFT_DANCE_FLOOR = pygame.USEREVENT + 4
PLAYER_DIED = pygame.USEREVENT + 5

OPEN_PROBLEM = pygame.USEREVENT + 6
PROBLEM_SOLVED = pygame.USEREVENT + 7
CHECK_PROBLEMS = pygame.USEREVENT + 8
CHECKED_PROBLEMS = pygame.USEREVENT + 9

USER_LOGIN = pygame.USEREVENT + 10

PROBLEM_DESCRIPTION = pygame.USEREVENT + 11

# Animation constants
PLAYER_SHEET_METADATA = {
    "frame_width": 16,
    "frame_height": 16,
    "scale": 4,
    "actions": {
        "idle": {
            "row": 0,
            "num_frames": 2,
            "cooldown": 500
        },
        "run" : {
            "row": 1,
            "num_frames": 6,
            "cooldown": 50
        },
        "jump" : {
            "row": 2,
            "num_frames": 4,
            "cooldown": 50
        },
        "punch" : {
            "row": 4,
            "num_frames": 3,
            "cooldown": 50
        }
    },
    "colorkey": (0, 0, 0)
}

ENEMY_SHEET_METADATA = {
    "frame_width": 64,
    "frame_height": 64,
    "scale": 2,
    "actions": {
        "idle": {
            "row": 1,
            "num_frames": 5,
            "cooldown": 500
        },
        "dead" : {
            "row": 0,
            "num_frames": 5,
            "cooldown": 500 
        },
        "walk" : {
            "row": 5,
            "num_frames": 7,
            "cooldown": 100
        },
        "headbutt" : {
            "row": 4,
            "num_frames": 4,
            "cooldown": 300
        }
    },
    "colorkey": (0, 0, 0)
}

WASD_SHEET_METADATA = {
    "frame_width": 96,
    "frame_height": 54,
    "scale": 2,
    "actions" : {
        "press": {
            "row": 0,
            "num_frames": 8,
            "cooldown": 500
        }
    },
    "colorkey": (0, 0, 0)
}

KEY_SHEET_METADATA = {
    "frame_width": 32,
    "frame_height": 32,
    "scale": 2,
    "actions": {
        "press": {
            "row": 0,
            "num_frames": 2,
            "cooldown": 500
        }
    },
    "colorkey": (0, 0, 0)
}

TEST_PLAYER_DICT = {
    "status": "success",
    "message": "retrieved",
    "totalSolved": 77,
    "totalQuestions": 3231,
    "easySolved": 23,
    "totalEasy": 813,
    "mediumSolved": 48,
    "totalMedium": 1697,
    "hardSolved": 6,
    "totalHard": 721,
    "acceptanceRate": 55.67,
    "ranking": 1145859,
    "contributionPoints": 106,
    "reputation": 0,
    "submissionCalendar": {
        "1695081600": 9,
        "1695168000": 1,
        "1695254400": 9,
        "1695600000": 4,
        "1696118400": 9,
        "1696636800": 9,
        "1697587200": 5,
        "1697673600": 6,
        "1697760000": 8,
        "1698019200": 3,
        "1698364800": 2,
        "1698624000": 6,
        "1698710400": 2,
        "1698796800": 6,
        "1699833600": 1,
        "1700092800": 9,
        "1700179200": 2,
        "1700438400": 3,
        "1705449600": 4,
        "1705536000": 3,
        "1705708800": 2,
        "1706054400": 1,
        "1706140800": 1,
        "1706745600": 3,
        "1707177600": 6,
        "1707264000": 1,
        "1707350400": 2,
        "1715212800": 3,
        "1715299200": 7,
        "1715385600": 9,
        "1715472000": 3,
        "1715644800": 1,
        "1715731200": 2,
        "1715817600": 1,
        "1716249600": 1,
        "1716336000": 1,
        "1716854400": 8,
        "1717459200": 3,
        "1717545600": 2,
        "1717632000": 6,
        "1717977600": 1,
        "1718236800": 1,
        "1718409600": 1,
        "1718755200": 1,
        "1719273600": 5,
        "1719360000": 4,
        "1719792000": 4,
        "1719964800": 1,
        "1720051200": 2,
        "1720224000": 3,
        "1720310400": 1,
        "1720483200": 2,
        "1720656000": 1,
        "1721260800": 1,
        "1722038400": 2
    }
}
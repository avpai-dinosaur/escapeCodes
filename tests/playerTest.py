"""Unit tests for the Player class."""

import unittest
from unittest.mock import patch
import pygame
from src.entities.player import Player
from src.entities.objects import LaserDoor

class TestMovement(unittest.TestCase):
    """Test the WASD movement of the player."""

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.mockPlayerSpritesheet = pygame.Surface((50, 50))
        with patch("src.core.utils.load_png") as mockImageLoad:
            mockImageLoad.return_value = (self.mockPlayerSpritesheet, self.mockPlayerSpritesheet.get_rect())
            self.player = Player("", (0, 0), None)

    @patch("pygame.key.get_pressed")
    def test_move_up(self, mockGetPressed):
        oldY = self.player.pos.y
        mockGetPressed.return_value = {
            pygame.K_w: 1,
            pygame.K_a: 0,
            pygame.K_s: 0,
            pygame.K_d: 0,
            pygame.K_p: 0,
            pygame.K_k: 0
        }
        self.player.update([], [])
        self.assertLess(self.player.pos.y, oldY)
    
    @patch("pygame.key.get_pressed")
    def test_move_left(self, mockGetPressed):
        oldX = self.player.pos.x
        mockGetPressed.return_value = {
            pygame.K_w: 0,
            pygame.K_a: 1,
            pygame.K_s: 0,
            pygame.K_d: 0,
            pygame.K_p: 0,
            pygame.K_k: 0
        }
        self.player.update([], [])
        self.assertLess(self.player.pos.x, oldX)

    @patch("pygame.key.get_pressed")
    def test_move_down(self, mockGetPressed):
        oldY = self.player.pos.y
        mockGetPressed.return_value = {
            pygame.K_w: 0,
            pygame.K_a: 0,
            pygame.K_s: 1,
            pygame.K_d: 0,
            pygame.K_p: 0,
            pygame.K_k: 0
        }
        self.player.update([], [])
        self.assertGreater(self.player.pos.y, oldY)

    @patch("pygame.key.get_pressed")
    def test_move_right(self, mockGetPressed):
        oldX = self.player.pos.x
        mockGetPressed.return_value = {
            pygame.K_w: 0,
            pygame.K_a: 0,
            pygame.K_s: 0,
            pygame.K_d: 1,
            pygame.K_p: 0,
            pygame.K_k: 0
        }
        self.player.update([], [])
        self.assertGreater(self.player.pos.x, oldX)
    
    @patch("pygame.key.get_pressed")
    def test_wall_collision(self, mockGetPressed):
        oldX = self.player.pos.x
        wall = pygame.Rect(
            self.player.rect.left + self.player.rect.width,
            self.player.rect.top, 1, 1)
        mockGetPressed.return_value = {
            pygame.K_w: 0,
            pygame.K_a: 0,
            pygame.K_s: 0,
            pygame.K_d: 1,
            pygame.K_p: 0,
            pygame.K_k: 0
        }
        self.player.update([wall], [])
        self.assertEqual(oldX, self.player.pos.x)
    
    @patch("pygame.key.get_pressed")
    def test_closed_door_collision(self, mockGetPressed):
        oldX = self.player.pos.x
        door = LaserDoor(
            pygame.Rect(
                self.player.rect.left + self.player.rect.width,
                self.player.rect.top, 1, 1
            )
        )
        mockGetPressed.return_value = {
            pygame.K_w: 0,
            pygame.K_a: 0,
            pygame.K_s: 0,
            pygame.K_d: 1,
            pygame.K_p: 0,
            pygame.K_k: 0
        }
        self.player.update([], [door])
        self.assertEqual(oldX, self.player.pos.x)
    
    @patch("pygame.key.get_pressed")
    def test_open_door_collision(self, mockGetPressed):
        oldX = self.player.pos.x
        door = LaserDoor(
            pygame.Rect(
                self.player.rect.left + self.player.rect.width,
                self.player.rect.top, 1, 1
            )
        )
        door.toggle = False
        mockGetPressed.return_value = {
            pygame.K_w: 0,
            pygame.K_a: 0,
            pygame.K_s: 0,
            pygame.K_d: 1,
            pygame.K_p: 0,
            pygame.K_k: 0
        }
        self.player.update([], [door])
        self.assertLess(oldX, self.player.pos.x)

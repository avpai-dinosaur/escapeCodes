"""Unit tests for the Player class."""

import unittest
from unittest.mock import patch
import pygame
from src.entities.player import Player

class TestMovement(unittest.TestCase):

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
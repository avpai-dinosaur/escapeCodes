"""Unit tests for the PseudocodeComputer class."""

import pygame
import unittest
from src.entities.computer import PseudocodeComputer

class TestParsing(unittest.TestCase):
    """Test the parsing of text into the computer."""

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_basic_parsing(self):
        text = (
f"""L1
{PseudocodeComputer.HiddenLineWord} L2
    L3"""
        )
        computer = PseudocodeComputer(pygame.Rect(0, 0, 10, 10), text)
        self.assertTrue(1 in computer.missingLines)
        self.assertEqual(
            computer.get_text(),
"""L1
**
    L3"""
        )

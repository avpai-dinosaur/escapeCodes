"""Unit tests for the SnippableComputer class."""

import pygame
import unittest
from src.entities.computer import SnippableComputer

class TestParsing(unittest.TestCase):
    """Test the parsing of text into the computer."""

    def setUp(self):
        pygame.init()
        pygame.display.set_mode((1, 1))

    def test_basic_probe(self):
        text = (
f"""L1
{SnippableComputer.PhraseStartWord} L2 {SnippableComputer.PhraseEndWord}
    L3"""
        )
        computer = SnippableComputer(pygame.Rect(0, 0, 10, 10), text)
        self.assertEqual(computer.try_probe(0), None)
        self.assertEqual(computer.try_probe(1), "L2")
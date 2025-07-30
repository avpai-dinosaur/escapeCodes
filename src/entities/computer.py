"""
computer.py
Classes representing different interactive computer entities in the game.
"""

import pygame
from src.components.ui import KeyPromptUi
from src.core.ecodeEvents import EcodeEvent, EventManager
import src.constants as c
import src.core.utils as utils

class Computer(pygame.sprite.Sprite):
    """Class to represent a computer."""

    def __init__(self, rect, textInput):
        super().__init__()
        self.rect = rect
        self.scaled_rect = rect.inflate(50, 50)
        self.textInput = textInput

        # Open button
        self.open_note_button = pygame.K_m
        self.keyPromptUi = KeyPromptUi(self.open_note_button, "Keys/M-Key.png", c.SM_KEY_SHEET_METADATA)
        self.keyPromptUi.rect.bottom = self.rect.top - 10
        self.keyPromptUi.rect.centerx = self.rect.centerx
        
        self.present_button = False
    
    def computer_action(self):
        self.present_button = False
        EventManager.emit(EcodeEvent.OPEN_NOTE, text=self.textInput)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.open_note_button and self.present_button:
                self.computer_action()

    def update(self, player):
        self.present_button = self.scaled_rect.colliderect(player.rect)
        if self.present_button:
            self.keyPromptUi.update()

    def draw(self, surface, offset):
        if self.present_button:
            self.keyPromptUi.draw(surface, offset)


class ProblemComputer(Computer):
    """Class to represent a computer that hosts a LeetCode problem."""

    def __init__(self, rect, textInput, url, pinText):
        super().__init__(rect, textInput)
        self.url = url
        self.problemSlug = None
        self.isSolved = False
        self.pinText = pinText
        # TODO: Remove this
        if self.url != "https://www.google.com/":
            self.problemSlug = utils.get_problem_slug(url)

        # Event subscribers
        EventManager.subscribe(EcodeEvent.PROBLEM_SOLVED, self.on_problem_solved)
    
    def on_problem_solved(self, problemSlug : str):
        if problemSlug == self.problemSlug:
            self.isSolved = True
            self.open_note()

    def computer_action(self):
        self.present_button = False
        if not self.isSolved:
            EventManager.emit(EcodeEvent.CHECK_PROBLEMS)
        self.open_note()
    
    def open_note(self):
        EventManager.emit(
            EcodeEvent.OPEN_NOTE,
            text=self.textInput,
            url=self.url,
            isSolved=self.isSolved,
            pinText=self.pinText
        )


class PseudocodeComputer(Computer):
    """Class to represent a computer that hosts a pseudocode problem."""

    HiddenLineWord = "HIDDENLINE"

    def __init__(self, rect, text: str):
        super().__init__(rect, text)
        self.lines = []
        self.missingLines = set()
        self._parse_text(text)

    def _parse_text(self, text: str):
        for idx, line in enumerate(text.split("\n")):
            parsedLine = []
            for word in line.split(" "):
                if word == PseudocodeComputer.HiddenLineWord:
                    self.missingLines.add(idx)
                else:
                    parsedLine.append(word)
            self.lines.append(" ".join(parsedLine))

    @staticmethod
    def anonymize_line(line):
        res = ""
        for c in line:
            if c == "\t":
                res += c
            else:
                res += "*"
        return res

    def get_text(self):
        embellishedLines = self.lines.copy()
        for line in self.missingLines:
            embellishedLines[line] = PseudocodeComputer.anonymize_line(self.lines[line])
        return "\n".join(embellishedLines)

    def computer_action(self):
        self.present_button = False
        EventManager.emit(EcodeEvent.OPEN_PSEUDOCODE, text=self.get_text(), problemSlug="two-sum")


class SnippableComputer(Computer):

    PhraseStartWord = "STARTPHRASE"
    PhraseEndWord = "ENDPHRASE"

    def __init__(self, rect, text):
        super().__init__(rect, text)
    
        self.phrases = []
        self.lines = []
        self.words = []
        self.showIndices = False
        self._parse_text(text)
    
    def _parse_text(self, text):
        wordIdx = 0
        currentPhrase = None

        for line in text.split("\n"):
            self.lines.append([])
            for word in line.split(" "):
                if word == SnippableComputer.PhraseStartWord:
                    if currentPhrase is not None:
                        raise ValueError("Attempted to start new phrase before closing current one")
                    currentPhrase = [wordIdx]
                elif word == SnippableComputer.PhraseEndWord:
                    if currentPhrase is None:
                        raise ValueError("Attempted to close phrase before starting one")
                    currentPhrase.append(wordIdx)
                    self.phrases.append(currentPhrase.copy())
                    currentPhrase = None
                else:
                    self.lines[-1].append(word)
                    self.words.append(word)
                    wordIdx += 1

    def get_phrase(self, wordIdx):
        for phrase in self.phrases:
            if phrase[0] <= wordIdx < phrase[1]:
                return phrase
        return None

    def try_probe(self, wordIdx):
        phrase = self.get_phrase(wordIdx)
        if phrase is not None:
            return " ".join(self.words[phrase[0]:phrase[1]])
        return None

    def get_text(self):
        return "\n".join([" ".join(line) for line in self.lines])
    
    def get_text_with_indices(self):
        idx = 0
        modifiedLines = []
        for line in self.lines:
            modifiedLine = []
            for word in line:
                modifiedLine.append(f"{word}({idx})")
                idx += 1
            modifiedLines.append(" ".join(modifiedLine))
        return "\n".join(modifiedLines)

    def computer_action(self):
        self.present_button = False
        if self.showIndices:
            EventManager.emit(EcodeEvent.OPEN_DOWNLOAD, text=self.get_text_with_indices())
        else:
            EventManager.emit(EcodeEvent.OPEN_NOTE, text=self.get_text())
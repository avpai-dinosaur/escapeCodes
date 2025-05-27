"""
chat.py
"""

import pygame
import src.core.utils as utils
from src.components.scrollable import ScrollableContainerUi

class ChatUi:
    def __init__(self, width, height):
        self.font = utils.load_font("SpaceMono/SpaceMono-Regular.ttf", size=15)
        self.scrollableContainer = ScrollableContainerUi(width, height, self.font.size("c")[1])
        self.history = []
    
    def add_message(self, message, isUser):
        self.history.append((message, isUser))  
    
    

    

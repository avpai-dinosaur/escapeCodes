"""Utility functions for loading assets and animations."""

import pygame
import sys
from pathlib import Path
import src.config as config

def load_png(filename):
    """Load image and return image object."""
    try:
        image = pygame.image.load(resource_path(config.IMAGE_DIR / filename))
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except FileNotFoundError:
        print(f"Cannot load image: {config.IMAGE_DIR / filename}")
        raise SystemExit
    return image, image.get_rect()

def load_animation(filename, x_size, y_size, num_frames):
    """Extract images from spritesheet.
    
    Returns a list of images which can be looped through
    to render an animation.
    """
    animation_list = []
    for frame in range(0, num_frames):
        temp_img = filename.subsurface(frame * x_size, 0, x_size, y_size)
        animation_list.append(temp_img)
    return animation_list

def resource_path(relativePath: str):
    """Get the absolute path to the resource.
    
        Works both for development and PyInstaller.
    """
    try:
        basePath = ""
        if getattr(sys, 'frozen', False):
            # Running in a bundled executable
            basePath = sys._MEIPASS
        else:
            # Running in a normal Python environment
            basePath = Path(__file__).resolve().parent.parent.parent
        
        return basePath / relativePath
    except Exception as e:
        print("Error resolving resource path:", e)
        return None
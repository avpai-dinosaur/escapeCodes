"""Utility functions for loading assets and animations."""

import pygame
import sys
import os

def load_png(filename):
    """Load image and return image object."""
    try:
        image = pygame.image.load(resource_path(filename))
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except FileNotFoundError:
        print(f"Cannot load image: {filename}")
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

def resource_path(relative_path):
    """Get the absolute path to the resource.
    
        Works both for development and PyInstaller.
    """
    try:
        base_path = ""
        if getattr(sys, 'frozen', False):
            # Running in a bundled executable
            base_path = sys._MEIPASS
        else:
            # Running in a normal Python environment
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print("Error resolving resource path:", e)
        return None
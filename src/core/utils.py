"""Utility functions for loading assets and animations."""

import pygame
import src.config as config

def load_png(filename):
    """Load image and return image object."""
    try:
        image = pygame.image.load(config.resource_path(config.IMAGE_DIR / filename))
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
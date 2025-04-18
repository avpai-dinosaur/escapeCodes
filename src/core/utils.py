"""Utility functions for loading assets and animations."""

import pygame
import platform
import os
import webbrowser
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

def load_font(filename, size=20):
    """Load a font from the assets directory."""
    try:
        font = pygame.Font(config.FONT_DIR / filename, size)
    except FileNotFoundError:
        print(f"Cannot load font: {config.FONT_DIR / filename}")
    return font 

def lighten_color(color: pygame.Color, amount=30):
    """Lightens a given Pygame color by increasing its RGB values."""
    r = min(color.r + amount, 255)
    g = min(color.g + amount, 255)
    b = min(color.b + amount, 255)
    return pygame.Color(r, g, b)

def open_url(url: str):
    """Open a url in the browser."""
    system = platform.system()
    if 'microsoft' in platform.uname().release.lower():  # WSL
        try:
            os.system(f"cmd.exe /c start {url}")
        except Exception as e:
            print(f"[WSL] Failed to open URL: {e}")
    elif system == "Windows":
        try:
            os.startfile(url)
        except Exception as e:
            print(f"[Windows] Failed to open URL: {e}")
    else:
        try:
            # Will use xdg-open or open depending on the system
            webbrowser.open(url)
        except Exception as e:
            print(f"[Linux/macOS] Failed to open URL: {e}")

def get_problem_slug(leetcodeProblemUrl: str):
    """Given a Leetcode url to a problem get the problem slug."""
    return leetcodeProblemUrl.split('/')[4]
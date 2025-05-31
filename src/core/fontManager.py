"""
fontCache.py
"""


import src.core.utils as utils


class FontManager:
    fonts = {}

    def get_font(filename, size):
        """Initialize a font or get it from the cache if it already exists."""
        k = (filename, size)
        if k not in FontManager.fonts:
            FontManager.fonts[k] = utils.load_font(filename, size)
        return FontManager.fonts[k]
        
        
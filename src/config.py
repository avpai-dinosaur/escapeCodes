import sys
from pathlib import Path

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
            basePath = Path(__file__).resolve().parent.parent
        
        return basePath / relativePath
    except Exception as e:
        print("Error resolving resource path:", e)
        return None

BASE_DIR = resource_path("")
ASSETS_DIR = BASE_DIR / "assets"
IMAGE_DIR = ASSETS_DIR / "images"
MAP_DIR = ASSETS_DIR / "map"

import pygame
import src.core.utils as utils

class SpriteSheet():
    """Represents a sprite sheet."""

    def __init__(self, sheet, metadata):
        """Constructor.
        
            sheet: png image of the sprite sheet.
            metadata: dictionary of metadata to help load the spritesheet.
        """
        self.sheet, _ = utils.load_png(sheet)
        self.metadata = metadata
        self.animations = {}
        self.parse_animations()

    def parse_frame(self, row, col):
        """Grabs an individual frame from the spritesheet.
        
            row, col: the row and column of the image in the spritsheet
        """
        width = self.metadata["frame_width"]
        height = self.metadata["frame_height"]
        color = self.metadata["colorkey"]
        scale = self.metadata["scale"]

        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(
            self.sheet,
            (0,0),
            ((col * width), (row * height), width, height)
        )
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(color)
        return image

    def parse_animations(self):
        """Parses all animations from the sprite sheet into self.animations."""
        for key, val in self.metadata["actions"].items():
            self.animations[key] = {}
            self.animations[key]["num_frames"] = val["num_frames"]
            self.animations[key]["images"] = []
            for i in range(val["num_frames"]):
                self.animations[key]["images"].append(
                    self.parse_frame(val["row"], i)
                )
    
    def get_image(self, action, frame):
        """Returns the image for the given action and frame.
        
            action: str
            frame: int
        """
        return self.animations[action]["images"][frame]
    
    def num_frames(self, action):
        """Returns the number of frames for this action.
        
            action: str
        """
        return self.animations[action]["num_frames"]

    def cooldown(self, action):
        """Returns the cooldown for the action.
        
            action: str
        """
        return self.metadata["actions"][action]["cooldown"]
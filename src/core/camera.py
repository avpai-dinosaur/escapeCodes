import pygame
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.constants as c


class Camera(pygame.sprite.Group):
    """Represents the world's camera"""

    def __init__(self):
        """Constructor."""
        super().__init__()
        self.background = None
        self.offset = pygame.math.Vector2()
        self.half_w = c.SCREEN_WIDTH // 2
        self.half_h = c.SCREEN_HEIGHT // 2

        # Camera positioning
        self.target = None

        # Zoom
        self.zoom = 1
        self.internal_surface_size = (c.SCREEN_WIDTH, c.SCREEN_HEIGHT)
        self.internal_surface = pygame.Surface(self.internal_surface_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surface.get_rect(center=(self.half_w, self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surface_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surface_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surface_size[1] // 2 - self.half_h
        self.x_bound_distance = self.half_w
        self.y_bound_distance = self.half_h

        # Lighting
        self.light_radius = 300
        self.dim = False

        # Event subscribers
        EventManager.subscribe(EcodeEvent.PLAYER_MOVED, self.set_target)

        self.foreground_objects = pygame.sprite.Group()
        self.background_objects = pygame.sprite.Group()
    
    def reset(self):
        """Clears all sprites the camera is managing.
        
            Usually called when loading a new level.
        """
        self.empty()
        self.foreground_objects.empty()
        self.background_objects.empty()

    def center_camera(self):
        """Centers the camera onto stored target."""
        self.offset.x = self.target.centerx - self.half_w
        self.offset.y = self.target.centery - self.half_h

    def set_target(self, target: pygame.Rect):
        """Set the camera's target."""
        self.target = target

    def update(self):
        """Update the camera."""
        if self.target:
            self.center_camera()

    def handle_event(self, event):
        """Handle an event off the event queue."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self.zoom = 2.5
            elif event.key == pygame.K_e:
                self.zoom = 1
        elif event.type == c.ENTERED_DANCE_FLOOR:
            self.dim = True
        elif event.type == c.LEFT_DANCE_FLOOR:
            self.dim = False

    def draw(self, surface):
        """Draw the sprites belonging to the camera group to surface."""
        # Draw to the camera's internal surface
        self.internal_surface.fill((0, 0, 0))
        self.internal_surface.blit(self.background, -self.offset + self.internal_offset)
        [obj.draw(self.internal_surface, -self.offset + self.internal_offset)
         for obj in self.background_objects]
        for sprite in sorted(self.sprites(), key=lambda s : s.rect.centery):
            sprite.draw(self.internal_surface, -self.offset + self.internal_offset)
        [obj.draw(self.internal_surface, -self.offset + self.internal_offset) 
         for obj in self.foreground_objects]
        
        # Scale image to zoom level
        scaled_surface = pygame.transform.scale(self.internal_surface, self.zoom * self.internal_surface_size_vector)
        scaled_rect = scaled_surface.get_rect(center=(self.half_w, self.half_h))
        surface.blit(scaled_surface, scaled_rect)

        # Dance floor
        dim_surface = pygame.Surface((1280, 800), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 180))  # RGBA: Dark transparent overlay
        if self.dim:
            surface.blit(dim_surface, (0, 0))
import pygame
from src.core.ecodeEvents import EventManager, EcodeEvent
import src.constants as c
import random
import math


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
        self.internal_surface = pygame.Surface(self.internal_surface_size, pygame.SRCALPHA).convert_alpha()
        self.internal_rect = self.internal_surface.get_rect(center=(self.half_w, self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surface_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surface_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surface_size[1] // 2 - self.half_h
        self.x_bound_distance = self.half_w
        self.y_bound_distance = self.half_h

        # Shake effect
        self.shakeDuration = None
        self.maxShakeIntensity = None
        self.shakeStart = None

        # Blackout effect
        self.blackoutDuration = None
        self.blackoutStart = None

        # Alarm effect
        self.alarmStart = None 
        self.alarmColor = (255, 0, 0)
    
        # Lighting
        self.brightness = 0

        # Event subscribers
        EventManager.subscribe(EcodeEvent.PLAYER_MOVED, self.set_target)
        EventManager.subscribe(EcodeEvent.CAMERA_SHAKE, self.shake)
        EventManager.subscribe(EcodeEvent.CAMERA_BLACKOUT, self.blackout)
        EventManager.subscribe(EcodeEvent.CAMERA_ALARM, self.alarm)

        self.foreground_objects = pygame.sprite.Group()
        self.background_objects = pygame.sprite.Group()
    
    def reset(self):
        """Clears all sprites the camera is managing.
        
            Usually called when loading a new level.
        """
        self.empty()
        self.foreground_objects.empty()
        self.background_objects.empty()
    
    def destroy(self):
        self.reset()
        EventManager.unsubscribe(EcodeEvent.PLAYER_MOVED, self.set_target)
        EventManager.unsubscribe(EcodeEvent.CAMERA_SHAKE, self.shake)
        EventManager.unsubscribe(EcodeEvent.CAMERA_BLACKOUT, self.blackout)
        EventManager.unsubscribe(EcodeEvent.CAMERA_ALARM, self.alarm)

    def center_camera(self):
        """Centers the camera onto stored target."""
        self.offset.x = self.target.centerx - self.half_w
        self.offset.y = self.target.centery - self.half_h
        if (
            self.shakeStart
            and pygame.time.get_ticks() - self.shakeStart < self.shakeDuration
        ):
            shakeIntensityScale = (pygame.time.get_ticks() - self.shakeStart) / self.shakeDuration
            intensity = self.maxShakeIntensity * shakeIntensityScale
            self.offset.x += random.uniform(-intensity, intensity)
            self.offset.y += random.uniform(-intensity, intensity)

    def set_target(self, target: pygame.Rect):
        """Set the camera's target."""
        self.target = target
    
    def shake(self, duration, maxIntensity):
        """Execute shake effect."""
        self.shakeDuration = duration
        self.maxShakeIntensity = maxIntensity
        self.shakeStart = pygame.time.get_ticks()
    
    def blackout(self, duration):
        """Execute blackout followed by fade in effect."""
        self.blackoutDuration = duration
        self.blackoutStart = pygame.time.get_ticks()
    
    def alarm(self):
        self.alarmStart = pygame.time.get_ticks()

    def update(self):
        """Update the camera."""
        if self.target:
            self.center_camera()
        if (
            self.blackoutStart
            and pygame.time.get_ticks() - self.blackoutStart < self.blackoutDuration
        ):
            timePassed = pygame.time.get_ticks() - self.blackoutStart
            normalized = timePassed / self.blackoutDuration
            blackoutIntensityScale = 1 if normalized < 0.3 else 1 - (normalized - 0.3) / 0.7
            self.brightness = 0 + 255 * blackoutIntensityScale
        elif self.alarmStart:
            timePassed = (pygame.time.get_ticks() - self.alarmStart) / 1000
            self.brightness = (26 + 24 * math.sin(2 * math.pi * timePassed * 0.5)) # 1 oscillations every 2 seconds between [2, 50]

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

        # Tweak lighting
        dim_surface = pygame.Surface((c.SCREEN_WIDTH, c.SCREEN_HEIGHT), pygame.SRCALPHA).convert_alpha()
        dimColor = self.alarmColor if self.alarmStart else (0, 0, 0)
        dim_surface.fill((dimColor[0], dimColor[1], dimColor[2], self.brightness)) 
        surface.blit(dim_surface, (0, 0))
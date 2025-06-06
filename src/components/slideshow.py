"""
slideshow.py
"""

import pygame
import src.core.utils as utils
import src.constants as c

class SlideshowUi:
    def __init__(self, width: int, height: int, slides: list[pygame.Surface]):
        self.rect = pygame.Rect(0, 0, width, height)

        self.slides = [pygame.transform.scale(slide, self.rect.size) for slide in slides]
        self.currentSlide = 0
        self.slideRect = self.slides[self.currentSlide].get_rect()

        self.rightArrow = pygame.transform.scale(
            utils.load_png("rightArrow.png")[0],
            (50, 50)
        )
        self.leftArrow = pygame.transform.flip(self.rightArrow, True, False)
        self.rightArrowRect = self.rightArrow.get_rect()
        self.leftArrowRect = self.leftArrow.get_rect()
        self.rightArrowRect.bottomright = self.rect.bottomright
        self.leftArrowRect.bottomleft = self.rect.bottomleft

        self.internalSurface = pygame.Surface(self.rect.size, pygame.SRCALPHA).convert_alpha()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.currentSlide = min(self.currentSlide + 1, len(self.slides) - 1)
            elif event.key == pygame.K_LEFT:
                self.currentSlide = max(0, self.currentSlide - 1)

    def draw(self, surface: pygame.Surface):
        self.internalSurface.fill((0, 0, 0, 0))
        self.internalSurface.blit(self.slides[self.currentSlide], self.slideRect)
        self.internalSurface.blit(self.rightArrow, self.rightArrowRect)
        self.internalSurface.blit(self.leftArrow, self.leftArrowRect)
        surface.blit(self.internalSurface, self.rect)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("Slideshow")
    clock = pygame.time.Clock()
    
    slides = [
        utils.load_png("titleSlide.png")[0],
        utils.load_png("secondSlide.png")[0]
    ]
    slideshow = SlideshowUi(480, 270, slides)
    slideshow.rect.centerx = c.SCREEN_WIDTH // 2
    slideshow.rect.centery = c.SCREEN_HEIGHT // 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            slideshow.handle_event(event)

        screen.fill("black")
        slideshow.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


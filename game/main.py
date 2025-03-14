import pygame

# Pygame needs to be initialized before other modules can be imported
pygame.init()

from manager import GameManager
import constants as c


def main(screen):
    pygame.display.set_caption("EscapeCodes")
    clock = pygame.time.Clock()
    manager = GameManager()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            manager.handle_event(event)
        
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        manager.update()
        manager.draw(screen)

        # flip() the display to put work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

if __name__ == "__main__":
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    main(screen)
    pygame.quit()

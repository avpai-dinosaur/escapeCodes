import os
import pygame
import src.config as config

# Pygame needs to be initialized before other modules can be imported
pygame.init()

from src.core.manager import GameManager
import src.constants as c

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
    print("Launching EscapeCodes from:", os.getcwd())
    print("\tBASE_DIR:", config.BASE_DIR)
    print("\tASSETS_DIR:", config.ASSETS_DIR)
    print("\tIMAGE_DIR:", config.IMAGE_DIR)
    print("\tMAP_DIR:", config.MAP_DIR)
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    main(screen)
    pygame.quit()

"""
scrollable.py
"""

import pygame
import src.core.utils as utils
import src.constants as c

class ScrollableContainerUi:
    """Class representing a scrollable container ui element."""

    def __init__(self, width: int, height: int, scrollDistance: int=5):
        """Constructor.
            
            width: Width of the scrollable container.
            height: Height of the scrollable container.
            scrollDistance: Number of pixels to scroll by.
        """
        self.rect = pygame.Rect(0, 0, width, height)
        self.internalSurface = pygame.Surface(self.rect.size, pygame.SRCALPHA).convert_alpha()
        self.scrollDistance = scrollDistance
        self.scrollBarTrackWidth = 10

    def set_content(self, content: pygame.Surface):
        """Set the contents of the scrollable container.
        
            content: Content the container should display.
        """
        self.content = content
        self.contentRect = content.get_rect()

        # Create the scroll bar
        self.scrollBar = None
        self.showScrollBar = False
        if self.contentRect.height > self.rect.height:
            self.scrollBar = pygame.Rect()
            self.scrollBar.width = self.scrollBarTrackWidth
            self.scrollBar.height = self.internalSurface.height ** 2 // self.contentRect.height
            self.scrollBar.top = 0
            self.scrollBar.right = self.internalSurface.width

    def update(self):
        self.showScrollBar = utils.is_mouse_in_rect(self.rect)

    def handle_event(self, event: pygame.Event):
        if event.type == pygame.MOUSEWHEEL and utils.is_mouse_in_rect(self.rect):
            scroll = (
                (event.y < 0 and self.contentRect.bottom > self.rect.height)
                or (event.y > 0 and self.contentRect.top < 0)
            )
            if scroll:
                distanceY = event.y * self.scrollDistance 
                self.contentRect.top += distanceY
                self.scrollBar.top = -(self.contentRect.top * self.internalSurface.height) // self.contentRect.height
    
    def draw(self, surface: pygame.Surface):
        self.internalSurface.fill((0, 0, 0, 0))
        self.internalSurface.blit(self.content, self.contentRect)
        if self.scrollBar and self.showScrollBar:
            pygame.draw.rect(self.internalSurface, "grey", self.scrollBar)
        surface.blit(self.internalSurface, self.rect)


class ScrollableTextUi:
    """Class representing scrollable text ui element."""

    def __init__(
        self,
        pos: pygame.Vector2,
        width: int,
        height: int,
        font: pygame.Font,
        color = "white"
    ):
        """Constructor.
        
            pos: Coordinates of left top corner of the element.
            width: Width of the element.
            height: Height of the element.
            font: Font to render text with.
            color: Color to render text in.
        """
        self.font = font
        self.color = color
        self.scrollableContainer = ScrollableContainerUi(width, height, self.font.size("c")[1])
        self.scrollableContainer.rect.topleft = pos
        self.set_text("")
    
    def set_text(self, textInput: str):
        self.text = textInput
        self.textImage = self.font.render(
            self.text, True, self.color,
            wraplength=self.scrollableContainer.rect.width - self.scrollableContainer.scrollBarTrackWidth
        )
        self.scrollableContainer.set_content(self.textImage)
    
    def update(self):
        self.scrollableContainer.update()

    def handle_event(self, event: pygame.Event):
        self.scrollableContainer.handle_event(event)
        
    def draw(self, surface: pygame.Surface):
        self.scrollableContainer.draw(surface)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
    pygame.display.set_caption("Scrollable")
    clock = pygame.time.Clock()
    
    scrollableText = ScrollableTextUi(
        pygame.Vector2(0, 0),
        c.SCREEN_WIDTH // 4,
        c.SCREEN_HEIGHT // 2,
        pygame.font.SysFont("calibri", 20)
    )
    textInput = (
        """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis maximus quam id tristique volutpat. Mauris commodo hendrerit metus id accumsan. Nam tempus erat id sem egestas, at sollicitudin ante bibendum. Duis eget rhoncus tellus. Morbi a tellus massa. Quisque facilisis tellus vitae nunc ornare, non malesuada diam lacinia. Nulla eget sapien eget lacus scelerisque laoreet eu eu ligula. Vestibulum bibendum sem leo, molestie iaculis nulla dapibus sit amet. Maecenas vitae sodales lacus, ac efficitur ligula. Suspendisse potenti. Phasellus nec tristique neque. Curabitur pulvinar vel libero vel malesuada. Curabitur id sodales ligula.

Sed ullamcorper eu augue sed feugiat. In tempor justo lacus, eu scelerisque enim hendrerit eu. Integer ac convallis nunc. Proin tincidunt nisi eros, ut ultrices ligula venenatis mattis. Duis nec aliquam lorem, a fermentum velit. In et sodales nulla, ultricies dignissim nisi. Ut tempor augue et turpis elementum finibus. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse elit turpis, facilisis et auctor non, tempor in arcu. Vivamus blandit neque et tincidunt blandit. Fusce tempus justo elit, ut tempus purus dictum vitae.

Aenean eget gravida turpis, non porttitor ante. In eu faucibus ligula. Nulla nec ultricies magna, nec accumsan justo. Sed elementum congue sapien at condimentum. Duis viverra nulla auctor felis vulputate, et euismod ante malesuada. Vivamus tempor vulputate tortor et tincidunt. Quisque at est porta, elementum purus ut, cursus felis. Integer dignissim velit quis lectus malesuada, ut varius tellus laoreet.

Integer ultrices in tortor vitae molestie. Maecenas consequat, eros porta tincidunt vestibulum, diam dui scelerisque magna, non vehicula diam lorem ac turpis. Nam lacinia vehicula tortor, sit amet cursus nisl volutpat nec. Proin a suscipit turpis. Nam ut purus id lorem suscipit fringilla. Duis convallis erat purus, a lacinia erat facilisis vel. Nunc sodales magna eget leo faucibus eleifend. Nullam tempus nibh vel nunc malesuada iaculis. Ut viverra, nisi nec faucibus interdum, risus odio luctus erat, et convallis tellus nisi eu neque. Suspendisse risus tortor, ullamcorper quis neque venenatis, eleifend interdum libero. Cras risus urna, ultrices eu feugiat nec, porttitor vitae risus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Proin sit amet nisl venenatis, commodo ipsum pretium, porta sapien. Suspendisse quis enim commodo, consequat sem sed, ornare erat.

Phasellus sodales in diam vel ullamcorper. Praesent gravida, ante vitae mollis rutrum, erat tellus commodo turpis, non luctus tellus enim a lorem. Proin ac urna nulla. Quisque ut fringilla dui. Mauris fringilla odio sed scelerisque consequat. Sed sit amet enim eget ligula euismod mattis et convallis mi. Duis dictum purus eget rhoncus aliquam. Nulla eleifend erat ut ante aliquet sagittis. Nunc eget nunc accumsan, tempor nibh maximus, ornare nibh. In sodales nisi eu dui consequat bibendum.
        """
    )
    scrollableText.set_text(textInput)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scrollableText.handle_event(event)

        scrollableText.update()
        
        screen.fill("black")
        scrollableText.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
import pygame
import src.core.utils as utils
from src.core.fontManager import FontManager

class Button:
	"""Represents a button on a game menu."""

	def __init__(
		self, image, pos, textInput, 
		font=None,
		baseColor="white",
		hoveringColor="red",
		onClick=lambda : None 
	):
		"""Constructor.

			image: Background image for the button.
			pos: Position of the button on screen.
			textInput: Text to render on button.
			font: pygame.Font to use when rendering button text.
			baseColor: Default color to render button text in.
			hoveringColor: Color to render button text in during mouse over.
		"""
		self.onClick = onClick
		self.pos = pos

		if font is None:
			self.font = FontManager.get_font("SpaceMono/SpaceMono-Regular.ttf", 40)
		else:
			self.font = font
		self.baseColor = baseColor
		self.hoveringColor = hoveringColor

		self.textInput = textInput
		self.text = self.font.render(self.textInput, True, self.baseColor)
		self.text_rect = self.text.get_rect(center=(self.pos))

		self.image = image
		# TODO: Fix this
		if self.image is None:
			self.image = self.text
		self.image_rect = self.image.get_rect(center=(self.pos))


	def check_mouseover(self, mousePosition):
		"""Returns True if the player's mouse is over the button.
		
			mousePosition: Current position of player's mouse.
		"""
		return (
			mousePosition[0] in range(self.image_rect.left, self.image_rect.right)
		  	and mousePosition[1] in range(self.image_rect.top, self.image_rect.bottom)
		)

	def change_color(self, mousePosition):
		"""Change color of button's text based on mouse position.

			mousePosition: Current position of player's mouse.
		"""
		if self.check_mouseover(mousePosition):
			self.text = self.font.render(self.textInput, True, self.hoveringColor)
		else:
			self.text = self.font.render(self.textInput, True, self.baseColor)

	def handle_event(self, event):
		"""Handle a click from the user."""
		mousePosition = pygame.mouse.get_pos()
		if self.check_mouseover(mousePosition) and event.type == pygame.MOUSEBUTTONDOWN:
			self.onClick()

	def update(self, mousePosition):
		"""Update state of the button."""
		self.change_color(mousePosition)
	
	def draw(self, surface):
		"""Draw the button to the surface.
		
			surface: The pygame.Surface to blit the button on.
		"""
		if self.image is not None:
			surface.blit(self.image, self.image_rect)
		surface.blit(self.text, self.text_rect)

class TextInput:
	def __init__(
		self, pos, width, height,
		activeColor=pygame.Color('red'),
		inactiveColor=pygame.Color('white'),
		font=None,
		inputTextColor='white',
		onSubmit=lambda x : None
	):
		"""Constructor.
		
			pos: Position of text input on screen.
			width: Width of the text input box.
			height: Height of the text input box.
			activeColor: Color of input box border when typing inside.
			inactiveColor: Color of input box border when not typing.
			font: Font of the text being typed.
			inputTextColor: Color of the text being typed.
			onSubmit: Callback function for when user presses Enter key.
		"""
		if font is None:
			self.font = FontManager.get_font("SpaceMono/SpaceMono-Regular.ttf", 30)
		else:
			self.font = font
		self.inputTextColor = inputTextColor
		self.activeColor = activeColor
		self.inactiveColor = inactiveColor
		self.hoverColor = utils.lighten_color(activeColor, 100)
		self.color = self.inactiveColor
		self.minWidth = width
		self.rect = pygame.Rect(0, 0, width, height)
		self.rect.center = pos
		self.active = False
		self.textBuffer= ""
		self.onSubmit = onSubmit
	
	def check_mouseover(self, mousePosition):
		"""Returns True if the player's mouse is over the text input field.
		
			mousePosition: Current position of player's mouse.
		"""
		return (
			mousePosition[0] in range(self.rect.left, self.rect.right)
		  	and mousePosition[1] in range(self.rect.top, self.rect.bottom)
		)

	def handle_event(self, event):
		"""Handle text input from the user."""
		if event.type == pygame.MOUSEBUTTONDOWN:
			mousePos = pygame.mouse.get_pos()
			if self.active and not self.check_mouseover(mousePos):
				self.active = False
			elif not self.active and self.check_mouseover(mousePos):
				self.active = True
			self.color = self.activeColor if self.active else self.inactiveColor
		elif (
			event.type == pygame.KEYDOWN
			and self.active
		):
			if event.key == pygame.K_RETURN:
				oldTextBuffer = self.textBuffer
				self.onSubmit(oldTextBuffer)
			elif event.key == pygame.K_BACKSPACE:
				self.textBuffer = self.textBuffer[:-1]
			else:
				self.textBuffer += event.unicode

	def update(self, mousePosition):
		if not self.active:
			if self.check_mouseover(mousePosition):
				self.color = self.hoverColor
			else:
				self.color = self.inactiveColor
	
	def draw(self, surface):
		"""Draw the text input control."""
		inputTextImage = self.font.render(self.textBuffer, True, self.inputTextColor)
		inputTextRect = inputTextImage.get_rect()
		self.rect.width = max(self.minWidth, inputTextRect.width)
		inputTextRect.bottomleft = self.rect.bottomleft

		pygame.draw.rect(surface, self.color, self.rect, width=2)
		surface.blit(inputTextImage, inputTextRect)
		
class ToggleButton(Button):
    def __init__(
        self, pos, size=(20, 20),
        initial_state=True,
        baseColor="white",
        toggleColor="black",
        outlineColor="white",
        onToggle=lambda state: None
    ):
        super().__init__(
            image=None,
            pos=pos,
            textInput="",
            baseColor=baseColor,
            onClick=self.toggle
        )
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = pos
        self.state = initial_state
        self.toggleColor = toggleColor
        self.outlineColor = outlineColor
        self.onToggle = onToggle

    def toggle(self):
        self.state = not self.state
        self.onToggle(self.state)

    def draw(self, surface):
        if self.state:
            pygame.draw.rect(surface, pygame.Color(self.baseColor), self.rect)
        else:
            pygame.draw.rect(surface, pygame.Color(self.toggleColor), self.rect)
            pygame.draw.rect(surface, pygame.Color(self.outlineColor), self.rect, width=2)

    def check_mouseover(self, mousePosition):
        return self.rect.collidepoint(mousePosition)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.toggle()

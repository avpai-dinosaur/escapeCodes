import pygame

class Button:
	"""Represents a button on a game menu."""

	def __init__(
		self, image, pos, textInput, 
		font=pygame.font.SysFont("cambria", 40),
		baseColor="#d7fcd4",
		hoveringColor="White",
		onClick=lambda : None 
	):
		"""Constructor.

			menu: Menu that the button belongs to.
			image: Background image for the button.
			pos: Position of the button on screen.
			font: pygame.Font to use when rendering button text.
			baseColor: Default color to render button text in.
			hoveringColor: Color to render button text in during mouse over.
			textInput: Text to render on button.
		"""
		self.onClick = onClick
		self.pos = pos

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
		activeColor=pygame.Color('azure3'),
		inactiveColor=pygame.Color('darkgoldenrod4'),
		font=pygame.font.SysFont("cambria", 50),
		inputTextColor='lightsalmon4',
		onSubmit=lambda : None
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
		self.font = font
		self.inputTextColor = inputTextColor
		self.activeColor = activeColor
		self.inactiveColor = inactiveColor
		self.color = self.inactiveColor
		self.rect = pygame.Rect(pos[0], pos[1], width, height)
		self.active = False
		self.textBuffer= ''
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
		if not self.check_mouseover(pygame.mouse.get_pos()):
			return

		if not self.active and event.type == pygame.MOUSEBUTTONDOWN:
			self.active = True
			self.color = self.activeColor
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_RETURN:
				oldTextBuffer = self.textBuffer
				self.textBuffer = ''
				self.onSubmit(oldTextBuffer)
			elif event.key == pygame.K_BACKSPACE:
				self.textBuffer = self.textBuffer[:-1]
			else:
				self.textBuffer += event.unicode
	
	def update(self, mousePosition):
		pass
	
	def draw(self, surface):
		"""Draw the text input control."""
		inputTextImage = self.font.render(self.textBuffer, True, self.inputTextColor)
		inputTextRect = inputTextImage.get_rect()
		inputTextRect.topright = self.rect.topright

		pygame.draw.rect(surface, self.color, self.rect, width=2)
		surface.blit(inputTextImage, inputTextRect)
		
	
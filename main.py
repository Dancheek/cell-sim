import pygame

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

BG_COLOR = (37, 37, 37)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Cell simulator")

def main():
	screen.fill(BG_COLOR)
	pygame.display.flip()

class cell:
	pass

state = "idle"
while state != "quit":
	main()
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			state = "quit"

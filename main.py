import pygame
import cell

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

BG_COLOR = (37, 37, 37)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Cell simulator")


def main():
	screen.fill(BG_COLOR)
	pygame.display.flip()


state = "idle"
clock = pygame.time.Clock()
while state != "quit":
	main()
	clock.tick(30)
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			state = "quit"


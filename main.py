import pygame
# import Cell
import World

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

WORLD_WIDTH = 64
WORLD_HEIGHT = 64
CELL_WIDTH = 10
CELL_HEIGHT = 10
BG_COLOR = (37, 37, 37)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Cell simulator")


def main():
	screen.fill(BG_COLOR)
	for x in range(WORLD_WIDTH):
		for y in range(WORLD_HEIGHT):
			if world.cells[x][y] is not None:
				screen.fill(world.cells[x][y].color, pygame.rect.Rect(x * CELL_WIDTH, y * CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT))
	pygame.display.flip()


world = World.World(WORLD_WIDTH, WORLD_HEIGHT)
world.gen()

state = "idle"
clock = pygame.time.Clock()
while state != "quit":
	main()
	clock.tick(30)
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			state = "quit"

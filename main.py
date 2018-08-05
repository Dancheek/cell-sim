from random import randint
from random import choice
import pygame

# -----= Some constants =-----

GENOME_SIZE = 64
ENERGY_LIMIT = 200


SOLAR_POWER = 32
SOLAR_FADING = 2

FIELD_EMPTY = 0
FIELD_WALL = 1
FIELD_CELL = 2

TICK_TIME = 30
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

GENOME_START_ENERGY = 100

WORLD_WIDTH = 64
WORLD_HEIGHT = 64
CELL_WIDTH = 10
CELL_HEIGHT = 10
BG_COLOR = (37, 37, 37)

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Cell simulator")


# //////////////////////////////////
# ----------[ Cell class ]----------

class Cell:
	def __init__(self, x, y, color, parent_genome=None):
		self.x = x
		self.y = y
		self.energy = GENOME_START_ENERGY
		self.genome_pointer = 0
		self.color = color

		if parent_genome is not None:
			self.genome = parent_genome
			if randint(1, 4) == 4:
				self.genome[randint(0, 63)] = randint(0, 63)
		else:
			self.genome = [23 for i in range(GENOME_SIZE)]

	def get_genome_content(self, index):
		if index >= GENOME_SIZE:
			return self.genome[index - GENOME_SIZE]
		return self.genome[index]

	def do_step(self):
		self.energy -= 3
		current_genome_content = self.get_genome_content(self.genome_pointer)

		if current_genome_content in genome_commands.keys():
			genome_commands[current_genome_content](self)
			# self.genome_pointer += shift
			# ты забыл self.genome_pointer++
		else:
			self.genome_pointer += current_genome_content

		if self.genome_pointer >= GENOME_SIZE:
			self.genome_pointer -= GENOME_SIZE 

		if self.energy >= ENERGY_LIMIT:
			self.create_child()

		if self.energy <= 0:
			self.die()

	def create_child(self):
		self.energy -= GENOME_START_ENERGY

		empty_spaces = []
		for delta_x, delta_y in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
			if world.field_type(self.x + delta_x, self.y + delta_y) == FIELD_EMPTY:
				empty_spaces.append((delta_x, delta_y))
		if not empty_spaces:
			self.die()
			return

		delta_x, delta_y = choice(empty_spaces)

		x, y = world.get_world_pos(self.x + delta_x, self.y + delta_y)
		world.cells[x][y] = Cell(x, y, self.color, self.genome)

	def die(self):
		world.cells[self.x][self.y] = None

# /////////////////////////////
# -----= Genome commands =-----

def photosynthesis(cell):
	cell.energy += world.get_light_energy(cell.x, cell.y)
	cell.genome_pointer += 1

def make_step(cell):
	cell.genome_pointer += 1

genome_commands = {
	23: photosynthesis,
	24: make_step,
}


# ///////////////////////////////////
# ----------[ World class ]----------

class World:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.world_reset()

	def world_reset(self):
		self.cells = [[None for y in range(self.height)] for x in range(self.width)]

	def get_world_pos(self, x, y):
		if x < 0:
			x += WORLD_WIDTH
		elif x >= WORLD_WIDTH:
			x -= WORLD_WIDTH
		return x, y#а по y мы должны тпшнуться типа слева выходишь справа заходишь

	def cells_spawn(self):
		for x in range(self.width):
			for y in range(self.height):
				if randint(1, 1000) == 1000:
					color = (0, 255-y*3.5, 0)
					self.cells[x][y] = Cell(x, y, color)

	def get_light_energy(self, x, y):
		energy = (SOLAR_POWER - y) / SOLAR_FADING
		if energy <= 0:
			return 0
		return energy

	def field_type(self, x, y):
		if y < 0 or y >= WORLD_HEIGHT:#я тупой, не понял зачем это(для чего, что это делает)
			return FIELD_WALL

		if x < 0: #get_world_pos()
			x += WORLD_WIDTH
		elif x >= WORLD_WIDTH:
			x -= WORLD_WIDTH

		if world.cells[x][y] is None:
			return FIELD_EMPTY

		return FIELD_CELL


# //////////////////////
# ------ Mainloop ------

def main():
	screen.fill(BG_COLOR)
	for x in range(WORLD_WIDTH):
		for y in range(WORLD_HEIGHT):
			if world.cells[x][y] is not None:
				screen.fill(world.cells[x][y].color, pygame.rect.Rect(x * CELL_WIDTH + 1, y * CELL_HEIGHT + 1, CELL_WIDTH - 2, CELL_HEIGHT - 2))
				world.cells[x][y].do_step()
	pygame.display.flip()


world = World(WORLD_WIDTH, WORLD_HEIGHT)
world.cells_spawn()

state = "idle"
clock = pygame.time.Clock()
while state != "quit":
	main()
	clock.tick(TICK_TIME)
	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			state = "quit"

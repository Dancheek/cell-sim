from random import randint
from random import random
from random import choice
import pygame

# -----= Some constants =-----

GENOME_SIZE = 16
GENOME_PARTS = 16
SPAWN_CHANCE = 1 / 1000
MUTATION_CHANCE = 1 / 40

ENERGY_LIMIT = 200

STEP_ENERGY_LOSS = 3

SOLAR_POWER = 32
SOLAR_FADING = 2

FIELD_EMPTY = 0
FIELD_WALL = 1
FIELD_CELL = 2

TICK_TIME = 30
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

CELL_START_ENERGY = 100

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
		self.energy = CELL_START_ENERGY
		self.genome_pointer = 0
		self.color = color

		if parent_genome is not None:
			self.genome = parent_genome
			if random() < MUTATION_CHANCE:
				self.genome[randint(0, GENOME_SIZE - 1)] = randint(0, GENOME_PARTS - 1)
		else:
			self.genome = [10 for i in range(GENOME_SIZE)]

		self.print_stats()

	def print_stats(self):
		print("x: %2s | y: %2s " % (self.x, self.y), end='[')
		for part in self.genome:
			if part < 10:
				print(part, end='')
			else:
				print(genome_characters[part], end='')
		print("]")

	def get_genome_content(self, index):
		if index >= GENOME_SIZE:
			return self.genome[index - GENOME_SIZE]
		return self.genome[index]

	def inc_genome_pointer(self, num):
		self.genome_pointer += num
		if self.genome_pointer >= GENOME_SIZE:
			self.genome_pointer -= GENOME_SIZE

	def do_step(self):
		self.energy -= STEP_ENERGY_LOSS
		current_genome_content = self.get_genome_content(self.genome_pointer)

		if (current_genome_content) in genome_commands.keys():
			genome_commands[current_genome_content](self)
		else:
			self.inc_genome_pointer(current_genome_content)

		while self.genome_pointer >= GENOME_SIZE:#переполнение может случиться из-за большого прыжка
			self.genome_pointer -= GENOME_SIZE

		if self.energy >= ENERGY_LIMIT:
			self.create_child()

		if self.energy <= 0:
			self.die()

	def create_child(self):
		self.energy -= CELL_START_ENERGY

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
	cell.inc_genome_pointer(1)

def make_step(cell):
	cell.inc_genome_pointer(1)

def change_color(cell):
	cell.color = (
		cell.get_genome_content(cell.genome_pointer + 1) * 16,
		cell.get_genome_content(cell.genome_pointer + 2) * 16,
		cell.get_genome_content(cell.genome_pointer + 3) * 16
	)
	cell.inc_genome_pointer(4)

def jmp(cell):
	cell.inc_genome_pointer(cell.get_genome_content(cell.genome_pointer + 1))

genome_commands = {
	10: photosynthesis,
	11: make_step,
	12: change_color,
	13: jmp,
}

genome_characters = {
	10: 'F',
	11: 'S',
	12: 'C',
	13: 'J',
	14: 'e',
	15: 'f'
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
		return x, y

	def cells_spawn(self):
		for x in range(self.width):
			for y in range(self.height):
				if random() < SPAWN_CHANCE:
					color = (0, 255-y*3.5, 0)
					self.cells[x][y] = Cell(x, y, color)

	def get_light_energy(self, x, y):
		energy = (SOLAR_POWER - y) / SOLAR_FADING
		if energy <= 0:
			return 0
		return energy

	def field_type(self, x, y):
		x, y = self.get_world_pos(x, y)

		if y < 0 or y >= WORLD_HEIGHT:
			return FIELD_WALL

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

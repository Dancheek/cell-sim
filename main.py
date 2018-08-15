from random import randint
from random import random
from random import choice
import pygame

# -----= Some constants =-----

GENOME_SIZE = 16
GENOME_PARTS = 16
SPAWN_CHANCE = 1 / 1000
MUTATION_CHANCE = 1 / 4

ENERGY_LIMIT = 1000

STEP_ENERGY_LOSS = 3

SOLAR_POWER = 32
SOLAR_FADING = 2

FIELD_EMPTY = 0
FIELD_WALL = 1
FIELD_CELL = 2
FIELD_DEAD_CELL = 3

FRAME_RATE = 100
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

CELL_START_ENERGY = 100
DEAD_CELL_ENERGY_VALUE = 30

WORLD_WIDTH = 64
WORLD_HEIGHT = 64
CELL_WIDTH = 10
CELL_HEIGHT = 10

DEAD_CELL_COLOR = (100, 100, 100)
BG_COLOR = (37, 37, 37)

DIRECTIONS = {      # 0   3   5
	0: (-1, -1),    #   \ | /
	1: (-1, 0),     # 1 - @ - 6
	2: (-1, 1),     #   / | \
	3: (0, -1),     # 2   4   7
	4: (0, 1),
	5: (1, -1),
	6: (1, 0),
	7: (1, 1)
}

COLOR_MODE_NATIVE = "native"
COLOR_MODE_ENERGY = "energy"

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Cell simulator")

pygame.font.init()
font = pygame.font.SysFont("consolas", 20)

def genome_mutate(genome):
	if random() < MUTATION_CHANCE:
		genome[randint(0, GENOME_SIZE - 1)] = randint(0, GENOME_PARTS - 1)
	return genome

# //////////////////////////////////
# ----------[ Cell class ]----------

class Cell:
	def __init__(self, x, y, color, parent_genome):
		self.x = x
		self.y = y
		self.energy = CELL_START_ENERGY
		self.genome_pointer = 0
		self.color = color
		self.alive = True
		self.direction = randint(0, 7)

		if parent_genome is not None:
			self.genome = parent_genome.copy()
			self.genome = genome_mutate(self.genome)
		else:
			self.genome = [10 for i in range(GENOME_SIZE)]

		print(self)

	def __str__(self):
		return "[{:<2} | {:<2}]  ({:<3} {:<3} {:<3})  [{}]  <{}>".format(self.x, self.y, int(self.color[0]), int(self.color[1]), int(self.color[2]), self.get_genome_string(), self.energy)

	def get_genome_string(self):
		genome_string = ''
		for part in self.genome:
			if part < 10:
				genome_string += str(part)
			else:
				genome_string += genome_characters[part]
		return genome_string

	def get_genome_content(self, index):
		if index >= GENOME_SIZE:
			return self.genome[index - GENOME_SIZE]
		return self.genome[index]

	def inc_genome_pointer(self, num=1):
		self.genome_pointer += num
		if self.genome_pointer >= GENOME_SIZE:
			self.genome_pointer -= GENOME_SIZE

	def do_step(self):
		commands_executed = 0
		exit_code = 0
		while True:
			if self.alive:
				self.energy -= STEP_ENERGY_LOSS
				current_genome_content = self.get_genome_content(self.genome_pointer)

				if (current_genome_content) in genome_commands.keys():
					exit_code = genome_commands[current_genome_content](self)
				else:
					self.inc_genome_pointer(current_genome_content)

				if self.genome_pointer >= GENOME_SIZE:
					self.genome_pointer -= GENOME_SIZE

				if self.energy <= 0:
					self.die()

				if self.energy >= ENERGY_LIMIT:
					self.create_child()

			else:
				world.move_cell(self.x, self.y, self.x, self.y + 1)
				break

			if exit_code == 1:
				break
			commands_executed += 1
			if commands_executed >= 10:
				break

	def create_child(self):
		self.energy -= CELL_START_ENERGY

		empty_spaces = []
		for direction in DIRECTIONS:
			x, y = world.get_pos_on_direction(self.x, self.y, direction)
			if world.get_field_type(x, y) == FIELD_EMPTY:
				empty_spaces.append((x, y))

		if not empty_spaces:
			self.die()
			return

		x, y = choice(empty_spaces)

		x, y = world.get_world_pos(x, y)
		world.create_cell(x, y, self.color, self.genome)

	def eat_cell(self, direction):
		target_x, target_y = world.get_pos_on_direction(self.x, self.y, direction)
		cell_type = world.get_field_type(target_x, target_y)

		if cell_type == FIELD_CELL:
			self.energy += DEAD_CELL_ENERGY_VALUE + world.cells[target_x][target_y].energy * 0.05
			world.remove_cell(target_x, target_y, True)

		elif cell_type == FIELD_DEAD_CELL:
			self.energy += DEAD_CELL_ENERGY_VALUE
			world.remove_cell(target_x, target_y)

	def die(self):
		self.energy = 0
		self.alive = False
		world.alive_count -= 1
		world.dead_count += 1


# /////////////////////////////
# -----= Genome commands =-----

def eat_cell(cell):
	cell.eat_cell(cell.direction)
	cell.inc_genome_pointer()
	return 1

def photosynthesis(cell):
	cell.energy += world.get_light_energy(cell.x, cell.y)
	cell.inc_genome_pointer()
	return 1

def make_step(cell):
	target_x, target_y = world.get_pos_on_direction(cell.x, cell.y, cell.direction)
	world.move_cell(cell.x, cell.y, target_x, target_y)
	cell.inc_genome_pointer()
	return 1

def change_color(cell):
	cell.color = (
		cell.get_genome_content(cell.genome_pointer + 1) * 16,
		cell.get_genome_content(cell.genome_pointer + 2) * 16,
		cell.get_genome_content(cell.genome_pointer + 3) * 16
	)
	cell.inc_genome_pointer(4)
	return 0

def move_genome_pointer(cell):
	cell.inc_genome_pointer(cell.get_genome_content(cell.genome_pointer + 1))
	return 0

def eat_dead_cells(cell):
	for direction in DIRECTIONS:
		x, y = world.get_pos_on_direction(cell.x, cell.y, direction)
		if world.get_field_type(x, y) == FIELD_DEAD_CELL:
			cell.eat_cell(direction)
	cell.inc_genome_pointer()
	return 1

def rotate_absolute(cell):
	cell.direction = cell.get_genome_content(cell.genome_pointer + 1) % 8
	cell.inc_genome_pointer(2)
	return 1


genome_commands = {
	9: eat_cell,
	10: photosynthesis,
	11: make_step,
	12: change_color,
	13: move_genome_pointer,
	14: eat_dead_cells,
	15: rotate_absolute
}

genome_characters = {
	10: 'F',
	11: 'S',
	12: 'C',
	13: 'J',
	14: 'E',
	15: 'R'
}


# ///////////////////////////////////
# ----------[ World class ]----------

class World:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.turn = 0
		self.cells_count = 0
		self.dead_count = 0
		self.alive_count = 0
		self.world_reset()

	def world_reset(self):
		self.cells = [[None for y in range(self.height)] for x in range(self.width)]

	def remove_cell(self, x, y, alive=False):
		self.cells[x][y] = None
		self.cells_count -= 1
		if alive:
			self.alive_count -= 1
		else:
			self.dead_count -= 1

	def create_cell(self, x, y, color, parent_genome=None):
		self.cells[x][y] = Cell(x, y, color, parent_genome)
		self.cells_count += 1
		self.alive_count += 1

	def move_cell(self, old_x, old_y, new_x, new_y):
		if self.get_field_type(new_x, new_y) == FIELD_EMPTY:
			self.cells[new_x][new_y] = self.cells[old_x][old_y]
			self.cells[old_x][old_y] = None
			self.cells[new_x][new_y].x = new_x
			self.cells[new_x][new_y].y = new_y

	def solar_flash(self):
		for x in range(self.width):
			for y in range(self.height):
				if world.cells[x][y] is not None:
					if random() < 0.5:
						world.cells[x][y].genome = genome_mutate(world.cells[x][y].genome)

	def get_world_pos(self, x, y):
		if x < 0:
			x += WORLD_WIDTH
		elif x >= WORLD_WIDTH:
			x -= WORLD_WIDTH
		return x, y

	def get_pos_on_direction(self, x, y, direction):
		delta_x, delta_y = DIRECTIONS[direction]
		return self.get_world_pos(x + delta_x, y + delta_y)

	def cells_spawn(self):
		for x in range(self.width):
			for y in range(self.height):
				if random() < SPAWN_CHANCE:
					color = (16, 16, 16)
					self.create_cell(x, y, color)
					# self.cells[x][y] = Cell(x, y, color)

	def get_light_energy(self, x, y):
		energy = (SOLAR_POWER - y) / SOLAR_FADING
		if energy < 0:
			return 0
		return round(energy)

	def get_field_type(self, x, y):
		x, y = self.get_world_pos(x, y)

		if y < 0 or y >= WORLD_HEIGHT:
			return FIELD_WALL

		if world.cells[x][y] is None:
			return FIELD_EMPTY

		if world.cells[x][y].alive:
			return FIELD_CELL

		return FIELD_DEAD_CELL

	def get_cell_color(self, x, y, color_mode):
		if color_mode == COLOR_MODE_NATIVE:
			return self.cells[x][y].color

		if color_mode == COLOR_MODE_ENERGY:
			cell_energy = self.cells[x][y].energy

			# if cell_energy > ENERGY_LIMIT / 2:
			# 	red = 255 - round(255 / (ENERGY_LIMIT / 2) * cell_energy / 2)
			# 	green = 255
			# else:
			# 	red = 255
			# 	green = round(255 / (ENERGY_LIMIT / 2) * cell_energy)
			if cell_energy <= 0:
				return DEAD_CELL_COLOR
			color = round(255 / ENERGY_LIMIT * cell_energy)
			if color < 0:
				color = 0
			elif color > 255:
				color = 255

			return (255, color, 0)


# //////////////////////
# ------ Mainloop ------

def main():
	m_x, m_y = pygame.mouse.get_pos()
	world_x = m_x // CELL_WIDTH
	world_y = m_y // CELL_HEIGHT

	screen.fill(BG_COLOR)

	for x in range(WORLD_WIDTH):
		for y in range(WORLD_HEIGHT):
			if world.cells[x][y] is not None:

				screen.fill(world.get_cell_color(x, y, simulation_color_mode), pygame.rect.Rect(x * CELL_WIDTH + 1, y * CELL_HEIGHT + 1, CELL_WIDTH - 2, CELL_HEIGHT - 2))

				if simulation_state != "paused":
					world.cells[x][y].do_step()

	if simulation_state != "paused":
		world.turn += 1

	if world.cells[world_x][world_y] is None:
		cell_string = "None"
	else:
		cell_string = "{} [{}] <{}>".format(
			world.get_cell_color(world_x, world_y, simulation_color_mode),
			world.cells[world_x][world_y].get_genome_string(),
			world.cells[world_x][world_y].energy
		)

	if menu_state == "shown":
		screen.blit(font.render("Cells: {} ({}/{})".format(world.cells_count, world.alive_count, world.dead_count), 1, (255, 255, 255)), (0, SCREEN_HEIGHT - 140))
		screen.blit(font.render("Turn: {}".format(world.turn), 1, (255, 255, 255)), (0, SCREEN_HEIGHT - 120))
		screen.blit(font.render("Color mode: {}".format(simulation_color_mode), 1, (255, 255, 255)), (0, SCREEN_HEIGHT - 100))
		screen.blit(font.render(cell_string, 1, (255, 255, 255)), (0, SCREEN_HEIGHT - 80))
		screen.blit(font.render("x: {:>2} | y: {:>2}".format(world_x, world_y), 1, (255, 255, 255)), (0, SCREEN_HEIGHT - 60))
		screen.blit(font.render(simulation_state, 1, (255, 255, 255)), (0, SCREEN_HEIGHT - 40))
		screen.blit(font.render("FPS: {}".format(round(clock.get_fps())), 1, (255, 255, 255)), (0, SCREEN_HEIGHT - 20))

	pygame.display.flip()


world = World(WORLD_WIDTH, WORLD_HEIGHT)
world.cells_spawn()

simulation_state = "idle"
menu_state = "shown"
simulation_color_mode = COLOR_MODE_NATIVE

clock = pygame.time.Clock()
while simulation_state != "quit":
	main()
	clock.tick(FRAME_RATE)

	for e in pygame.event.get():
		if e.type == pygame.QUIT:
			simulation_state = "quit"
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_SPACE:
				if simulation_state == "idle":
					simulation_state = "paused"
				elif simulation_state == "paused":
					simulation_state = "idle"
			if e.key == pygame.K_BACKQUOTE:
				if menu_state == "shown":
					menu_state = "hidden"
				elif menu_state == "hidden":
					menu_state = "shown"
			if e.key == pygame.K_1:
				simulation_color_mode = COLOR_MODE_NATIVE
			if e.key == pygame.K_2:
				simulation_color_mode = COLOR_MODE_ENERGY
			if e.key == pygame.K_m:
				world.solar_flash()

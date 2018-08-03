from random import randint
import Cell

SOLAR_POWER = 32
SOLAR_FADING = 2

def get_light_energy(x, y):
	energy = (SOLAR_POWER - y) / SOLAR_FADING
	if energy <= 0:
		return 0
	return energy


class World:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.world_reset()

	def world_reset(self):
		self.cells = [[None for y in range(self.height)] for x in range(self.width)]

	def gen(self):
		for x in range(self.width):
			for y in range(self.height):
				if randint(1, 1000) == 1000:
					print(x, y)
					color = (((x + 1) * (y + 1) - 1) % 255, 255, 0)
					self.cells[x][y] = Cell.Cell(x, y, color)

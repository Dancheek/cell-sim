from random import randint
import Cell

class World:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.world_reset()

	def world_reset(self):
		self.cells = [[None for y in range(self.height)] for x in range(self.width)]

	def gen(self, max_x, max_y):
		for x in range(max_x):
			for y in range(max_y):
				if randint(1, 1000) == 1:
					self.cells[x][y] = Cell.Cell(x, y)

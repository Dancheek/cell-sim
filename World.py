from random import randint
import Cell

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
				if randint(1, 1000) == 1:
					print(x, y)
                                        color = (255, 0, 0)
					self.cells[x][y] = Cell.Cell(x, y, color)

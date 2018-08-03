import World
from random import randint

GENOME_LENGHT = 64
ENERGY_LIMIT = 200

class Cell:
	def __init__(self, x, y, color, parent_genome=None):
		self.x = x
		self.y = y
		self.energy = 100
		self.genome_pointer = 0
		self.color = color

		if parent_genome is not None:
			self.genome = parent_genome
			if randint(1, 4) == 4:
				self.genome[randint(0, 63)] = randint(0, 63)
		else:
			self.genome = [23 for i in range(GENOME_LENGHT)]

	def get_genome_content(self, index):
		if index >= GENOME_LENGHT:
			return self.genome[index - GENOME_LENGHT]
		return self.genome[index]

	def do_step(self):
		current_genome_content = self.get_genome_content(self.genome_pointer)

		if current_genome_content in genome_commands.keys():
			genome_commands[current_genome_content](self)
			self.genome_pointer += 1
		else:
			self.genome_pointer += current_genome_content

		if self.genome_pointer >= GENOME_LENGHT:
			self.genome_pointer -= GENOME_LENGHT

		if self.energy >= ENERGY_LIMIT:
			self.create_child()

	def create_child(self):
		self.energy -= 100

# --------- Genome commands ----------

def photosynthesis(cell):
	cell.energy += World.get_light_energy(cell.x, cell.y)

genome_commands = {
	23: photosynthesis
}

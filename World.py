class World:
	def __init__(self, width, height):
		self.width = width
		self.height = height

        def reset(self):
            self.cells=NULL

        def gen(self,max_x,max_y):
            for(i=0; i<max_x; i++)
                for(j=0; j<max_y; j++)
                    #random 0..1000 -> if (res == 0) self.cells[i][j]=new_cell(i,j)
                    #


class Grid:

    'The main grid constructor'

    def __init__(self, window):
        self.grid = []
        self.fullgrid = []
        self.g = window
        self.path = []
        self.dim = self.g.grid_dim
        self.generate()
        self.grid = self.fullgrid
        self.start = (0, self.dim[1]//2)
        self.goal = (self.dim[0] - 1, self.dim[1]//2)

    def generate(self):
        self.fullgrid = []
        print "generating"
        for xi in range(0, self.dim[0]):
            for yi in range(0, self.dim[1]):
                self.fullgrid.append((xi, yi))

    # def generateHD(self):
    #     self.hd_grid = []
    #     g = self.g
    #     for iy in range(0, g.grid_dim[1] * 2):
    #         for ix in range(0, g.grid_dim[0] * 2):
    #             current = (ix // 2, iy // 2)
    #             if current in self.grid:
    #                 self.hd_grid.append((ix, iy))

    #     r_list = []
    #     for p in self.hd_grid: # Smooths corners by checking neighbor count
    #         n = get_neighbors(self.hd_grid, p[0], p[1])
    #         if len(n) <= 2:
    #             r_list.append(p)

    #     for r in r_list:
    #         self.hd_grid.remove(r)


    # def exportGrid(self):
    #     g = self.g
    #     self.generateHD()
    #     f = open(g.pf_exportfile, "w")
    #     f.write("{0} {1}\n".format(g.grid_dim[0], g.grid_dim[1]))
    #     for iy in range(0, g.grid_dim[1]):
    #         l = []
    #         s = ""
    #         for ix in range(0, g.grid_dim[0]):
    #             if [ix, iy] in self.hd_grid:
    #                 l.append("0")
    #             else:
    #                 l.append("1")

    #         for n in l:
    #             s += n
    #         f.write(s + "\n")
    #     f.close()

    # def importGrid(self):
    #     f = open(self.g.pf_importfile, "r")
    #     raw = f.readline()
    #     rawpoints = raw.split()
    #     points = []
    #     for p in rawpoints:
    #         np = p.split(",")
    #         newpoint = [int(np[0]), int(np[1])]
    #         points.append(newpoint)
    #     # points = expandPath(self.grid, points)
    #     return points

    # def update(self, new=True):
    #     self.debug = self.g.debug
    #     if self.debug:
    #         print("generating new grid")
    #     self.grid = self.fullgrid
    #     tc, wc = 0, 0
    #     for t in self.g.towers:
    #         for g in self.grid:  # Checks for towers in grid, removes them
    #             if t.gx == g[0] and t.gy == g[1]:
    #                 self.grid.remove(g)
    #                 tc += 1
    #     if self.debug:
    #         print("removed {0} grid points for towers".format(tc))
    #     for w in self.g.walls:
    #         for g in self.grid:  # Checks for towers in grid, removes them
    #             if w.gx == g[0] and w.gy == g[1]:
    #                 self.grid.remove(g)
    #                 wc += 1
    #     if self.debug:
    #         print("removed {0} grid points for walls".format(wc))
    #     if new:
    #         # x1, y1 = str(self.start[0]), str(self.start[1])
    #         # x2, y2 = str(self.goal[0]), str(self.goal[1])
    #         # subprocess.call(["./genpath", x1, y1, x2, y2])
    #         # points = self.importGrid()
    #         # self.path = points
    #         newpath = self.getPath(self.start)
    #         if newpath:
    #             self.path = newpath
    #         else:
    #             self.path = [self.goal]

    # def getPath(self, start):
    #     path, success = pypf.get_path(
    #             self.grid, self.fullgrid,
    #             start, self.goal
    #     )

    #     if success:
    #         return path
    #     else:
    #         return False

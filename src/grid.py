from main import pypf
import subprocess
from functions import get_neighbors


class Grid:

    'The main grid constructor'

    def __init__(self, game):
        self.t_grid = []
        self.w_grid = []
        self.fullgrid = []
        self.debug = game.debug
        self.g = game
        self.path = []
        self.dim = self.g.grid_dim
        self.generate()
        self.start = self.g.spawn
        self.goal = self.g.goal

    def generate(self):
        self.fullgrid = []
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

    def update(self, new="update"):
        self.debug = self.g.debug
        if self.debug:
            print("generating new grid")

        t_grid = []
        w_grid = []

        for p in self.fullgrid:
            t_grid.append(p)
            w_grid.append(p)
        tc, wc = 0, 0
        for w in self.g.tiles_no_walk:
            if w in w_grid:
                w_grid.remove(w)
                wc += 1
        for b in self.g.tiles_no_build:
            if b in t_grid:
                t_grid.remove(b)
                tc += 1
        for t in self.g.towers:
            for g in w_grid:  # Checks for towers in grid, removes them
                if t.gx == g[0] and t.gy == g[1]:
                    if (t.gx, t.gy) in t_grid:
                        t_grid.remove(g)
                    if (t.gx, t.gy) in w_grid:
                        w_grid.remove(g)
                    tc += 1
        if self.debug:
            print("removed {0} grid points for towers".format(tc))
        if self.debug:
            print("removed {0} grid points for no walk".format(wc))
        if new == "dry":
            old_w, old_t = self.w_grid, self.t_grid
            self.w_grid = w_grid
            self.t_grid = t_grid
            newpath = self.getPath(self.start)
            if newpath:
                self.path = newpath
                return True
            else:
                self.w_grid = old_w
                self.t_grid = old_t
                return False
        else:
            self.w_grid = w_grid
            self.t_grid = t_grid


        if new == "update":
            # x1, y1 = str(self.start[0]), str(self.start[1])
            # x2, y2 = str(self.goal[0]), str(self.goal[1])
            # subprocess.call(["./genpath", x1, y1, x2, y2])
            # points = self.importGrid()
            # self.path = points
            newpath = self.getPath(self.start)
            if newpath:
                self.path = newpath
            else:
                self.path = [self.goal]

    def getPath(self, start, flying=False):
        if flying:
            path, success = pypf.get_path(
                    self.fullgrid, self.fullgrid,
                    start, self.goal
            )
        else:
            path, success = pypf.get_path(
                    self.w_grid, self.w_grid,
                    start, self.goal
            )

        if success:
            return path
        else:
            return False

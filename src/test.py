import unittest

# import main
import functions

tcase = unittest.TestCase


class TestColorCodeConverter(tcase):

    def test_white(self):
        self.assertEqual(functions.get_color(255, 255, 255, 255), (1, 1, 1, 1))

    def test_red(self):
        self.assertEqual(functions.get_color(255, 0, 0, 255), (1, 0, 0, 1))

    def test_green(self):
        self.assertEqual(functions.get_color(0, 255, 0, 255), (0, 1, 0, 1))

    def test_blue(self):
        self.assertEqual(functions.get_color(0, 0, 255, 255), (0, 0, 1, 1))

    def test_transparent(self):
        self.assertEqual(
            functions.get_color(127, 84, 221, 70),
            (
                0.4980392156862745,
                0.32941176470588235,
                0.8666666666666667,
                0.27450980392156865
            )
        )


class TestCreateRectangle(tcase):

    def test_square(self):
        self.assertEqual(
            functions.create_rectangle(
                48, 48, 32, 32, centered=False
            ),
            [16, 48, 16, 16, 48, 16, 48, 48]
        )

    def test_rectangle(self):
        self.assertEqual(
            functions.create_rectangle(
                48, 48, 64, 32, centered=False
            ),
            [-16, 48, -16, 16, 48, 16, 48, 48]
        )

    def test_square_centered(self):
        self.assertEqual(
            functions.create_rectangle(
                48, 48, 32, 32, centered=True
            ),
            [32, 32, 32, 64, 64, 64, 64, 32],
        )

    def test_rectangle_centered(self):
        self.assertEqual(
            functions.create_rectangle(
                48, 48, 64, 32, centered=True
            ),
            [16, 32, 16, 64, 80, 64, 80, 32]
        )


class TestCheckPointInRectangle(tcase):

    def test_inside(self):
        rect = [32, 32, 32, 64, 64, 64, 64, 32]
        self.assertTrue(functions.check_point_rectangle(32, 32, rect))

    def test_outside(self):
        rect = [32, 32, 32, 64, 64, 64, 64, 32]
        self.assertFalse(functions.check_point_rectangle(63, 65, rect))


class Mob:

    """The main mob constructor, for testing"""

    def __init__(self, game):
        self.move_type = "normal"
        self.g = game
        self.hp = 14.0
        self.spd = 1.0
        self.debug = game.debug
        self.id = 0
        s = game.grid.start
        self.x = 0
        self.y = 0
        self.rx = 0
        self.ry = 0  # Real position, which is used in game logic
        self.state = "alive"
        self.slow_cd = None
        self.lastpoint = None
        self.stall_timer = None
        self.debuff_list = []
        self.currentpoint = s
        self.point = 0
        self.path = False
        if self.move_type == "flying":
            self.path = game.grid.getPath(self.currentpoint, flying=True)
        if not self.path:
            self.path = game.grid.path

        try:
            self.targetpoint = self.path[1]
        except IndexError:
            self.targetpoint = (0, 0)

def make_game_object(self):
    from grid import Grid
    self.debug = False
    self.grid_dim = (8, 8)
    self.spawn = (0, 0)
    self.goal = (8, 8)
    self.tiles_no_walk = [(4, 4), (4, 5), (5, 5), (5, 6), (6, 6)]
    self.tiles_no_build = [(4, 4), (4, 5), (5, 5), (5, 6), (6, 6)]
    self.flightgrid = []
    self.towers = []
    self.grid = Grid(self)
    self.grid.update("update")
    self.m = Mob(self)


class TestPathChecking(tcase):

    def test_update(self):
        make_game_object(self)
        self.assertTrue(
            functions.check_path(self.m, self.grid, (4, 4))
        )

    def test_not_update(self):
        make_game_object(self)
        self.assertFalse(
            functions.check_path(self.m, self.grid, (4, 5))
        )


class TestCheckDiagonal(tcase):

    def test_w_grid(self):
        make_game_object(self)
        self.assertEqual(
            functions.get_diagonal(self.grid.w_grid, 3, 3),
            [(4, 2), (2, 4), (2, 2)]
        )

    def test_t_grid(self):
        make_game_object(self)
        self.assertEqual(
            functions.get_diagonal(self.grid.t_grid, 3, 3),
            [(4, 2), (2, 4), (2, 2)]
        )

    def test_full_grid(self):
        make_game_object(self)
        self.assertEqual(
            functions.get_diagonal(self.grid.fullgrid, 3, 3),
            [(4, 4), (4, 2), (2, 4), (2, 2)]
        )


class TestGetNeighbors(tcase):

    def test_w_grid(self):
        make_game_object(self)
        self.assertEqual(
            functions.get_neighbors(self.grid.w_grid, 3, 3),
            [(4, 3), (3, 4), (2, 3), (3, 2)]
        )

    def test_t_grid(self):
        make_game_object(self)
        self.assertEqual(
            functions.get_neighbors(self.grid.t_grid, 3, 3),
            [(4, 3), (3, 4), (2, 3), (3, 2)]
        )

    def test_full_grid(self):
        make_game_object(self)
        self.assertEqual(
            functions.get_neighbors(self.grid.fullgrid, 3, 3),
            [(4, 3), (3, 4), (2, 3), (3, 2)]
        )


class TestExpandPath(tcase):

    def test(self):
        make_game_object(self)
        print functions.expandPath(self.grid.w_grid, self.grid.path)


def expandPath(grid, path):
    newpath = []
    for p in path:
        newpath.append(p)
        neighbors = get_neighbors(grid, p[0], p[1])
        diagonals = get_diagonal(grid, p[0], p[1])
        for d in diagonals:
            if not d in newpath:
                newpath.append(d)
        for n in neighbors:
            if not n in newpath:
                newpath.append(n)
    for n in newpath:
        if n[0] == 8:
            print(n)
    return newpath


def get_dist(x1, y1, x2, y2):  # Returns distance between to points
    x = (x1 - x2) * (x1 - x2)
    y = (y1 - y2) * (y1 - y2)
    dist = math.sqrt(x + y)
    return dist


def get_angle(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    rads = math.atan2(-dy, dx)
    rads %= 2*math.pi
    return rads


if __name__ == '__main__':
    unittest.main()

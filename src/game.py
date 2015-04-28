from functions import *
from grid import *
from mob import *
import pyglet

# Crappy map until TMX import is done -.-
NOWALK = [
    (17, 0), (17, 1), (17, 2), (17, 3), (17, 4), (17, 8), (17, 9), (17, 10), (17, 11),
    (17, 12), (17, 13), (17, 14), (17, 15), (17, 16), (18, 16), (19, 16), (20, 16),
    (21, 16), (21, 17),
    (21, 18), (21, 19), (21, 20), (22, 20), (23, 20), (24, 20), (25, 20), (26, 20),
    (27, 20), (28, 20), (29, 20), (30, 20), (31, 20), (32, 20), (33, 20), (34, 20),
    (35, 20), (23, 3), (23, 4), (23, 5), (23, 6), (23, 7), (23, 8), (23, 9), (23, 10),
    (23, 11), (23, 12), (24, 12), (25, 12), (26, 12), (27, 12), (27, 13), (27, 14),
    (27, 15),  (27, 16), (6, 7), (7, 7), (6, 8), (7, 8), (6, 9), (7, 9), (6, 10), (7, 10),
    (6, 11), (7, 11), (6, 12), (7, 12), (6, 13), (7, 13), (6, 14), (7, 14),
    (4, 18), (5, 18), (4, 19), (5, 19),
    (11, 6), (11, 5), (12, 5)
]
NOBUILD = [
    (6, 7), (7, 7), (6, 8), (7, 8), (6, 9), (7, 9), (6, 10), (7, 10),
    (6, 11), (7, 11), (6, 12), (7, 12), (6, 13), (7, 13), (6, 14), (7, 14),
    (4, 18), (5, 18), (4, 19), (5, 19)
]


class Game():

    """Game session."""

    def __init__(self, window):
        self.debug = window.debug
        self.window = window    # Need to keep track of the game window
        # Lists of game objects
        self.mobs = []  # Enemy mob sprite objects
        self.mob_count = 0  # This serve as mob's id
        self.towers = []  # Tower sprite objects
        self.selected_mouse = None  # Holds the object mouse is dragging
        self.dragging = False   # If an object is currently being dragged
        self.mouse_drag_tower = None
        self.active_tower = None   # List of highlighted items
        self.autospawn = False
        self.loaded = False     # If game is loaded
        self.paused = True      # Game starts off in a paused state

        # Economy
        self.gold = 0         # Players "wallet"
        self.total_value = 0    # To be used later for adaptive difficulty

        # Pathfinding stuff
        self.pf_queue = []
        self.pf_clusters = []

        # Specifies how the game grid will be, and calculates the offset
        self.generateGridSettings()

    def newGame(self, level="default"):

        print("Starting a new game.")

        # Generates grid parameters for game instance
        self.tiles_no_build = NOBUILD
        self.tiles_no_walk = NOWALK
        self.generateGridSettings()
        self.grid = Grid(self)

        # Remove old stuff from game window
        self.window.flushWindow()

        # Create particle emitters
        self.window.addParticleEmitters()

        # Lists of game objects
        self.mobs = []  # Enemy mob sprite objects
        self.mob_count = 0  # This serve as mob's id
        self.towers = []  # Tower sprite objects
        self.window.animations = []
        self.selected_mouse = None
        self.dragging = False
        self.highlighted = []
        self.gold = 100
        self.loaded = True
        pyglet.clock.unschedule(self.autospawn_random)
        pyglet.clock.schedule_interval(self.pathFinding, 1.0/60.0)

        # Autospawn random mob every second
        self.autospawn = False

        self.grid.update()

        # Adding buttons to UI
        for b in ("1", "2", "3"):
            self.window.userinterface.add_button(b)
        self.window.userinterface.add_text("gold")
        self.paused = False
        self.window.mainmenu = None   # Kills the menu

    def generateGridSettings(self):
        """ These control the grid that is the game window """
        w, h, gm, ssize = self.window.width, self.window.height, 0, 32
        self.squaresize = ssize
        self.grid_margin = gm
        self.grid_dim = (36, 21)
        self.window.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.window.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def updateGridSettings(self):
        w, h, gm, ssize = self.window.width, self.window.height, 0, 32
        self.window.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.window.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def pathFinding(self, dt, limit=1):
        if len(self.pf_queue) > 0:
            if len(self.pf_queue) >= 60:
                limit *= 2
            if self.debug:
                print("Calculating paths for pf_queue.")
                print("Length of queue: {0}.".format(len(self.pf_queue)))
            count = 0
            for m in self.pf_queue:
                if count == limit:
                    break
                m.updateTarget()
                self.pf_queue.remove(m)
                count += 1

        # for m in self.mobs:
        #     if m.state == "stalled":
        #         m.updateState()

    def place_tower(self, t, x, y, new=False):
        """Positions tower and updates game state accordingly."""
        placed = False
        grid = self.grid
        dist = self.window.height // 10  # Range to check for available square

        if t.price <= self.gold:
            for g in grid.t_grid:
                if not g == grid.goal or g == grid.start:
                    if x and y:
                        gx = self.window.get_windowpos(g[0], g[1])[0]
                        gy = self.window.get_windowpos(g[0], g[1])[1]
                        if get_dist(gx, gy, x, y) < dist:
                            dist = get_dist(gx, gy, x, y)
                            placed = False
                            if dist <= self.squaresize:
                                placed = True
                                new_g = g
                                new_rg = (gx, gy)

        if placed:
            self.gold -= t.price
            t.selected = False
            t.updatePos(new_rg[0], new_rg[1], new_g[0], new_g[1])
            if new:
                self.towers.append(t)
            print("Towers: {0}".format(len(self.towers)))

            update = False
            if new_g in grid.path:
                update = True
            else:
                for p in grid.path:
                    if new_g in get_diagonal(
                        grid.w_grid,
                        p[0], p[1]
                    ):
                        update = True
                        break
                    elif new_g in get_neighbors(
                        grid.w_grid,
                        p[0], p[1]
                    ):
                        update = True
                        break

            if update:
                for m in self.mobs:
                    if m not in self.pf_queue:
                        if check_path(m, grid.w_grid, new_g):
                            self.pf_queue.append(m)

            grid.update(new=update)
            # self.pathFinding(limit=100)

            if self.debug:
                print("New path for grid: {0}".format(update))

            if self.debug:
                print("Tower placed at [{0},{1}]".format(new_g[0], new_g[1]))

        elif t in self.towers:
            self.towers.remove(t)
            grid.update(new=False)

    def autospawn_random(self, dt):
        """Spawns a random mob"""
        if not self.paused:
            choice = random.randint(0, 2)
            if choice:
                mob = Mob(self, "YAY")
            else:
                mob = Mob1W(self, "YAY")

            self.mobs.append(mob)

    def updateState(self):
        for t in self.towers:
            if not t.target:  # if tower has no target
                i = random.randrange(0, 3)
                for m in self.mobs:
                    if(m.move_type in t.target_types):
                        dist = get_dist(m.x, m.y, t.x, t.y)
                        if dist <= t.range:
                            if i == 0:
                                t.target = m
                                break
            else:  # if tower has a target, do something
                dist = get_dist(t.target.x, t.target.y, t.x, t.y)
                if dist > t.range:
                    t.target = None

                if t.target not in self.mobs:
                    t.target = None

                if t.target:
                    if t.target.state == "alive":
                        rads = get_angle(t.x, t.y, t.target.x, t.target.y)
                        t.setAngle(rads)
                        t.doDamage(t.target)  # Do damage
                    if t.target.state == "dead":
                        t.target = None
            t.resetCD()

        for m in self.mobs:
            m.updatePos()  # Update movement
            m.updateState()  # Update mob state, e.g. "dead", "alive"

        if self.gold > 999:     # Maximum amount of gold
            self.gold = 999

    def get_total_value(self):
        value = 0
        for t in self.towers:
            value += t.price
        return value

    # def generateGridIndicators(self):
    #     """ Generates the squares that indicates available blocks """
    #     w = self.squaresize
    #     points = []
    #     rects = []
    #     for p in self.grid.w_grid:
    #         wp = self.window.get_windowpos(p[0], p[1])
    #         x = wp[0] - w // 2
    #         y = wp[1] - w // 2
    #         points.append(wp[0])
    #         points.append(wp[1])
    #         r_points = [x, y, x + w, y, x + w, y + w, x, y + w]
    #         rects = rects + r_points

from main import logger
from functions import *
from grid import *
from mob import *
from tiles import *
import pyglet
import os


class Game():

    """Game session."""

    def __init__(self, window):
        self.debug = window.debug
        self.window = window    # Need to keep track of the game window
        # Lists of game objects
        self.mobs = []  # Enemy mob sprite objects
        self.mobtier = 1
        self.mob_count = 0  # This serve as mob's id
        self.tower_count = 0  # This serve as towers's id
        self.towers = []  # Tower sprite objects
        self.available_towers = {
            "1": 10,
            "2": 25,
            "3": 40,
            "4": 70,
        }
        self.selected_mouse = None  # Holds the object mouse is dragging
        self.dragging = False   # If an object is currently being dragged
        self.mouse_drag_tower = None
        self.active_tower = None   # List of highlighted items
        self.autospawn = False
        self.loaded = False     # If game is loaded
        self.paused = True      # Game starts off in a paused state

        self.lives = 10

        # Economy
        self.gold = 0           # Players "wallet"
        self.ai_gold = 0        # Gold used to spawn mobs by AI
        self.total_value = 0    # To be used later for adaptive difficulty

        # Pathfinding stuff
        self.pf_queue = []
        self.pf_clusters = []

        # Specifies how the game grid will be, and calculates the offset
        # self.generateGridSettings()

        # player = pyglet.media.Player()
        # sound = pyglet.media.load('../resources/mus1.ogg')
        # player.queue(sound) 

        # # keep playing for as long as the app is running (or you tell it to stop):
        # player.eos_action = pyglet.media.Player.EOS_LOOP 

        # player.play()

    def newGame(self, level):

        logger.info("Starting a new game.")
        self.map = level
        # Display load screen
        self.window.mainmenu = None   # Kills the menu
        self.window.loading = True
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        self.window.render(0)
        self.window.flip()
        # Remove old stuff from game window
        self.window.flushWindow()

        # Generates grid parameters for game instance
        self.tiles_no_build = []
        self.tiles_no_walk = []
        self.flightgrid = []
        self.generateGridSettings()
        self.grid = Grid(self)

        self.window.tile_renderer.update_offset()

        # Create particle emitters
        self.window.addParticleEmitters()

        # Lists of game objects
        for m in self.mobs:
            m.debuff_list = []
        self.mobs = []  # Enemy mob sprite objects
        self.mob_count = 0  # This serve as mob's id
        for t in self.towers:
            t.target = None
        self.goal, self.spawn = None, None
        self.towers = []  # Tower sprite objects
        self.window.animations = []
        self.selected_mouse = None
        self.dragging = False
        self.highlighted = []
        self.active_tower = None
        self.mouse_drag_tower = None
        self.pf_queue = []
        self.gold = 25
        self.ai_gold = 0
        self.ai_flat_income = 0
        try:
            pyglet.clock.unschedule(self.aiIncome)
        except:
            pass
        try:
            pyglet.clock.unschedule(self.updateState)
        except:
            pass
        try:
            pyglet.clock.unschedule(self.autospawnBalanced)
        except:
            pass
        pyglet.clock.schedule_interval(
                        self.aiIncome,
                        10.0
                    )
        pyglet.clock.schedule_interval(
                        self.autospawnBalanced,
                        0.25
                    )
        self.lives = 10
        pyglet.clock.unschedule(self.autospawn_random)
        pyglet.clock.schedule_interval(self.pathFinding, 1.0/60.0)

        # Autospawn random mob every second
        self.autospawn = False

        self.grid.update(new="update")
        pyglet.clock.schedule_interval(self.updateState, 1.0/30.0)

        # Adding buttons to UI
        for b in ("1", "2", "3", "4", "gold_icon"):
            self.window.userinterface.add_button(b)
        self.window.userinterface.add_text("gold")
        self.window.loading = False
        self.loaded = True
        self.paused = False

    def generateGridSettings(self):
        """ These control the grid that is the game window """
        tiles = TiledRenderer(self.window, self.map)
        mw = tiles.tmx_data.width
        mh = tiles.tmx_data.height
        self.grid_dim = (mw, mh)
        w, h, gm = self.window.width, self.window.height, 0
        self.grid_margin = gm
        ssize = tiles.tmx_data.tilewidth
        self.squaresize = ssize
        self.window.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.window.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2
        self.window.tile_renderer = tiles

    def updateGridSettings(self):
        w, h, gm, ssize = self.window.width, self.window.height, \
            self.grid_margin, self.squaresize
        self.window.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.window.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def createGridIndicators(self):
        self.window._rectangles = pyglet.graphics.vertex_list(
            4,
            'v2i'
        )
        self.window._rectangles_path = pyglet.graphics.vertex_list(
            4,
            'v2i'
        )
        self.window.rectangles = []
        self.window.rectangles_path = []
        grid = []
        path = []
        for p in self.grid.t_grid:
            grid.append(p)
        for p in self.grid.path:
            try:
                grid.remove(p)
                path.append(p)
            except ValueError:
                pass
        for p in grid:
            pos = self.window.get_windowpos(p[0], p[1])
            x, y = pos
            ss = self.squaresize - 2
            rectangle = create_rectangle(x, y, ss, ss)
            self.window.rectangles.append(rectangle)

        for p in path:
            pos = self.window.get_windowpos(p[0], p[1])
            x, y = pos
            ss = self.squaresize - 6
            rectangle = create_rectangle(x, y, ss, ss)
            self.window.rectangles_path.append(rectangle)

        batch = self.window.batches["fg2"]
        for r in self.window.rectangles:
            # vertex_list = pyglet.graphics.vertex_list(4,
            #     ('v2i', r),
            #     ('c3B', [128, 128, 255, 80] * 4)
            # )
            self.window._rectangles = batch.add(
                4, pyglet.graphics.gl.GL_QUADS, None,
                ('v2i', r),
            )
        batch = self.window.batches["fg3"]
        for r in self.window.rectangles_path:
            self.window._rectangles_path = batch.add(
                4, pyglet.graphics.gl.GL_QUADS, None,
                ('v2i', r),
            )

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
        grid = self.grid
        placed = False

        if t.price <= self.gold:
            try:
                gx, gy = self.window.get_gridpos(x, y)
                if (gx, gy) in grid.t_grid:
                    placed = True
            except LookupError or ValueError as err:
                logger.debug("Available square not found: {0}".format(err))

        if placed:
            new_g = gx, gy
            new_rg = self.window.get_windowpos(gx, gy)
            self.gold -= t.price
            w_grid = grid.w_grid
            t_grid = grid.t_grid
            t.selected = False
            t.updatePos(new_rg[0], new_rg[1], new_g[0], new_g[1])
            t.id = self.tower_count
            self.tower_count += 1
            if new:
                self.towers.append(t)

                logger.debug("Towers: {0}".format(len(self.towers)))

                update = False
                if new_g in grid.path:
                    update = True
                else:
                    for p in grid.path:
                        if new_g in get_diagonal(
                            w_grid,
                            p[0], p[1]
                        ):
                            update = True
                            break
                        elif new_g in get_neighbors(
                            w_grid,
                            p[0], p[1]
                        ):
                            update = True
                            break

                if update:
                    for m in self.mobs:
                        if m not in self.pf_queue:
                            if check_path(m, w_grid, new_g):
                                self.pf_queue.append(m)

            if not grid.update(new="dry"):
                logger.warning("TOWER BLOCKING PATH")
                t.sell()

            # if grid.getPath(grid.start):
            # # self.pathFinding(limit=100)
            #     pass

            logger.debug("New path for grid: {0}".format(update))

            logger.debug("Tower placed at [{0},{1}]".format(new_g[0], new_g[1]))

        elif t in self.towers:
            self.towers.remove(t)
            grid.update(new=False)

        else:
            self.active_tower = None
            self.mouse_drag_tower = None
            self.selected_mouse = None

    def spawnMob(self, variant, free=False):
        # name = str(self.mobtier) + variant
        name = str(1) + variant
        options = {
            "1Q": Mob(self, name),
            "1W": Mob1W(self, name),
            "1E": Mob1E(self, name),
            "1R": Mob1R(self, name),
            "1A": Mob1A(self, name),
            "1S": Mob1S(self, name),
            "1D": Mob1D(self, name),
            "1F": Mob1F(self, name),
            "1Z": Mob1Z(self, name),
            "1X": Mob1X(self, name),
            "1C": Mob1C(self, name),
            "1V": Mob1V(self, name),
        }

        try:
            mob = options[name]
        except KeyError as err:
            logger.debug("Mob not found: {0}".format(err))
            return False
        if self.mobtier == 2:
            mob.hp_max *= 50
            mob.hp = mob.hp_max
            mob.bounty *= 50
        if mob.bounty * 2 <= self.ai_gold or free:
            if not free:
                self.ai_gold -= mob.bounty * 2

            self.mobs.append(mob)

    def autospawn_random(self, dt):
        """Spawns a random mob"""
        if not self.paused:
            choice = random.randint(0, 1)
            if choice:
                self.spawnMob("Q", free=True)
            else:
                self.spawnMob("E", free=True)

    def autospawnBalanced(self, dt):
        if not self.paused and self.ai_gold > 0:
            mob_choices = 12
            choice = random.randint(0, mob_choices - 1)
            if choice < mob_choices - 1 and len(self.mobs) >= 100:
                choice += 2
            mob = None
            if choice == 0:
                self.spawnMob("Q")
            elif choice == 1:
                self.spawnMob("W")
            elif choice == 2:
                self.spawnMob("E")
            elif choice == 3:
                self.spawnMob("R")
            elif choice == 4:
                self.spawnMob("A")
            elif choice == 5:
                self.spawnMob("S")
            elif choice == 6:
                self.spawnMob("D")
            elif choice == 7:
                self.spawnMob("F")
            elif choice == 8:
                self.spawnMob("Z")
            elif choice == 9:
                self.spawnMob("X")
            elif choice == 10:
                self.spawnMob("C")
            elif choice == 11:
                self.spawnMob("V")
            # if choice == 0:
            #     mob = Mob(self, "YAY")
            # elif choice == 1:
            #     mob = Mob1W(self, "YAY")
            # elif choice == 2:
            #     mob = Mob1E(self, "YAY")
            # elif choice == 3:
            #     mob = Mob1R(self, "YAY")
            # elif choice == 4:
            #     mob = Mob1A(self, "YAY")
            # elif choice == 5:
            #     mob = Mob1S(self, "YAY")
            # elif choice == 6:
            #     mob = Mob1D(self, "YAY")
            # elif choice == 7:
            #     mob = Mob1F(self, "YAY")
            # elif choice == 8:
            #     mob = Mob1Z(self, "YAY")
            # elif choice == 9:
            #     mob = Mob1X(self, "YAY")
            # elif choice == 10:
            #     mob = Mob1C(self, "YAY")
            # elif choice == 11:
            #     mob = Mob1V(self, "YAY")


    def aiIncome(self, dt):
        if not self.paused:
            self.ai_gold += self.ai_flat_income
            self.ai_flat_income += 1
            self.ai_gold += (self.get_total_value() + self.gold) // 10
            if self.ai_gold > 1600:
                self.mobtier = 2
            logger.info("AI current gold: {0}".format(self.ai_gold))

    def gameOver(self):
        logger.info("Game lost, returning to menu.")
        self.loaded = False
        self.paused = True
        for m in self.mobs:
            m.debuff_list = []
        self.mobs = []  # Enemy mob sprite objects
        self.mob_count = 0  # This serve as mob's id
        for t in self.towers:
            t.target = None
        self.goal, self.spawn = None, None
        self.towers = []  # Tower sprite objects
        self.window.animations = []
        self.selected_mouse = None
        self.dragging = False
        self.highlighted = []
        self.active_tower = None
        self.mouse_drag_tower = None
        self.pf_queue = []

        try:
            pyglet.clock.unschedule(self.aiIncome)
        except:
            pass
        try:
            pyglet.clock.unschedule(self.updateState)
        except:
            pass
        try:
            pyglet.clock.unschedule(self.autospawnBalanced)
        except:
            pass

        self.window.flushWindow()
        self.window.showMainMenu()

    def updateState(self, dt):
        if not self.paused:
            if self.lives <= 0:
                self.gameOver()
            for t in self.towers:
                if t.cd:
                    t.resetCD()
                if not t.target:  # if tower has no target
                    t.getTarget()
                else:
                    t.updateTarget()

            for m in self.mobs:
                m.updatePos(dt=dt)  # Update movement
                m.updateState()  # Update mob state, e.g. "dead", "alive"

            if self.gold > 9999:     # Maximum amount of gold
                self.gold = 9999

    def leaking(self):
        self.lives -= 1
        self.window.play_sfx("pluck")

    def get_total_value(self):
        value = 0
        for t in self.towers:
            value += t.price
        return value

import pyglet   # Version 1.2.2
from collections import OrderedDict
from pyglet.window import key, mouse
from pyglet.gl import *
from lepton import Particle, ParticleGroup, default_system
from lepton.emitter import StaticEmitter
from lepton.renderer import PointRenderer
from lepton.texturizer import SpriteTexturizer, create_point_texture
from lepton.controller import Gravity, Lifetime, Movement, Fader, ColorBlender, Growth
# import pytmx    # Tiled map loader

from functions import *
from grid import *


### Global variables ###
DEBUG = False
RES_PATH = "../resources/"
SCREENRES = (1280, 720)  # The resolution for the game window
VSYNC = True
PAUSED = False
SCREEN_MARGIN = 15  # %
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
    (4, 18), (5, 18), (4, 19), (5, 19)
]
NOBUILD = [
    (6, 7), (7, 7), (6, 8), (7, 8), (6, 9), (7, 9), (6, 10), (7, 10),
    (6, 11), (7, 11), (6, 12), (7, 12), (6, 13), (7, 13), (6, 14), (7, 14),
    (4, 18), (5, 18), (4, 19), (5, 19)
]
### Get information about the OS and display ###11
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

### Limit the frames per second to 60 ###
pyglet.clock.set_fps_limit(60)
fps_display = pyglet.clock.ClockDisplay()

############################
### Import classes ###
from tower import *
from mob import *
from ui import *
# from wall import *
from animation import *
from particles import *


class Game(pyglet.window.Window):  # Main game window

    def __init__(self):
        ### Template for multisampling
        gl_template = pyglet.gl.Config(
            sample_buffers=1,
            samples=2,
            alpha_size=8
            )
        self.debug = DEBUG
        try:  # to enable multisampling
            gl_config = screen.get_best_config(gl_template)
        except pyglet.window.NoSuchConfigException:
            gl_template = pyglet.gl.Config(alpha_size=8)
            gl_config = screen.get_best_config(gl_template)
            print("No multisampling.")
        ### Create OpenGL context ###
        gl_context = gl_config.create_context(None)
        super(Game, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=True,
            vsync=VSYNC
            )
        ### GL and graphics variables ###
        self.width = SCREENRES[0]
        self.height = SCREENRES[1]
        self.offset = (0, 0)
        self.cx, self.cy = 0, 0  # Cursor position
        glClearColor(0.1, 0.1, 0.1, 1)  # Background color
        # self.particle_system = default_system

        self.batches = OrderedDict()
        self.batches["mobs"] = pyglet.graphics.Batch()
        self.batches["bg"] = pyglet.graphics.Batch()
        self.batches["bg2"] = pyglet.graphics.Batch()
        self.batches["towers"] = pyglet.graphics.Batch()
        self.batches["buttons"] = pyglet.graphics.Batch()
        self.batches["mm_buttons"] = pyglet.graphics.Batch()
        # self.batches["walls"] = pyglet.graphics.Batch()
        self.batches["anim"] = pyglet.graphics.Batch()
        self.ui_group = pyglet.graphics.OrderedGroup(2)

        self.loadTextures()

        ### Particle group ###
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)

        ### Lists of game objects ###
        self.mobs = []  # Enemy mob sprite objects
        self.mob_count = 0  # This serve as mob's id
        self.towers = []  # Tower sprite objects
        # self.walls = []  # Wall sprite objects
        # self.placeWalls()  # Fills walls list and updates grid
        self.animations = []
        self.selected_mouse = None
        self.dragging = False
        self.highlighted = []

        ### Pathfinding stuff ###
        self.pf_queue = []
        self.pf_clusters = []
        self.paused = True

        self.generateGridSettings()

        print "Creating UI"
        self.userinterface = UI(self)

        # Spawn main menu
        self.mainmenu = MainMenu(self)
        self.mainmenu.add_entry(title="New Game", action="newgame")
        self.mainmenu.add_entry(title="Exit", action="quit")

        # Start a new game
        # self.newGame()


    def newGame(self, level="default"):

        print "Starting a new game."

        ### Generates grid parameters for game instance ###
        self.tiles_no_build = NOBUILD
        self.tiles_no_walk = NOWALK
        self.generateGridSettings()
        self.grid = Grid(self)

        self.bg_group = pyglet.graphics.OrderedGroup(0)
        self.fg_group = pyglet.graphics.OrderedGroup(1)

        ### Lists of game objects ###
        self.mobs = []  # Enemy mob sprite objects
        self.mob_count = 0  # This serve as mob's id
        self.towers = []  # Tower sprite objects
        self.animations = []
        self.selected_mouse = None
        self.dragging = False
        self.highlighted = []

        # Autospawn random mob every second
        self.autospawn = False
        try:
            print "Removing old particle system."
            pyglet.clock.unschedule(self.particle_system.update)
        except AttributeError:
            pass
        self.particle_system = default_system
        self.particle_system.run_ahead(2.0, 30.0)
        pyglet.clock.schedule_interval(self.particle_system.update, 1.0/30.0)
        pyglet.clock.schedule_interval(self.pathFinding, 1.0/10.0)

        # Particles and stuff
        self.puff_fx, self.smoke_fx, self.muzzle_fx, self.skull_fx = (
            None,
            None,
            None,
            None
        ) 
        self.puff_fx = ParticleCategory(self, "simple", "puff")
        self.smoke_fx = ParticleCategory(self, "simple", "smoke")
        self.muzzle_fx = ParticleCategory(self, "simple", "pang")
        self.skull_fx = ParticleCategory(self, "simple", "skull")
        self.flame_emitter, self.gas_emitter = None, None
        self.addParticleEmitters()
        self.bg = pyglet.sprite.Sprite(
            self.textures["bg"], batch=self.batches["bg"])
        self.bg.x = self.offset_x
        self.bg.y = self.offset_y

        self.grid.update()

        # Adding buttons to UI
        for b in ("1", "2", "3"):
            self.userinterface.add_button(b)
        self.paused = False


    def loadTextures(self):

        ### Get images from resource cache and centers their anchor points ###
        ws_img = center_image(pyglet.image.load(RES_PATH + 'wall_stone.png'))
        tw_img = center_image(pyglet.image.load(RES_PATH + 'tower_wood.png'))
        p_texture = pyglet.image.load(RES_PATH + 'particle.png')
        p_smoke_texture = pyglet.image.load(RES_PATH + 'particle_smoke.png')
        p_pang_texture = pyglet.image.load(RES_PATH + 'particle_pang.png')
        p_skull_texture = pyglet.image.load(RES_PATH + 'particle_skull.png')
        tp_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_poison.png')
        )
        tp_t_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_poison_turret.png')
        )
        ts_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_splash.png')
        )
        ts_t_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_splash_turret.png')
        )
        mob_1w = center_image(pyglet.image.load(RES_PATH + 'mob_1w.png'))
        mob_1q = center_image(pyglet.image.load(RES_PATH + 'mob.png'))
        bg01 = pyglet.image.load(RES_PATH + 'bg01.png')

        self.textures = dict(
            wall_stone=ws_img,
            tower_wood=tw_img,
            tower_poison=tp_img,
            tower_poison_turret=tp_t_img,
            tower_splash=ts_img,
            tower_splash_turret=ts_t_img,
            mob1Q=mob_1q,
            mob1W=mob_1w,
            bg=bg01
        )

        self.effects = dict(
            puff=p_texture,
            smoke=p_smoke_texture,
            skull=p_skull_texture,
            pang=p_pang_texture,
        )
        ### Load sprite sheet ###
        ### All credits go to http://opengameart.org/users/hyptosis ###
        sprite_sheet_img = pyglet.image.load(
            RES_PATH + 'hyptosis_tile-art-batch-1.png')
        sprite_sheet = pyglet.image.ImageGrid(
            sprite_sheet_img,
            sprite_sheet_img.width / 32, sprite_sheet_img.height / 32)
        for i in sprite_sheet:
            i = center_image(i)
        self.spritesheet = sprite_sheet

        ### Load images and create image grids for animations ###
        ### and centers their frame anchor point              ###
        death_img = pyglet.image.load(RES_PATH + 'mob_death.png')
        pang_img = pyglet.image.load(RES_PATH + 'pang_01_32.png')
        death_anim = pyglet.image.ImageGrid(death_img, 1, 7)
        pang_anim = pyglet.image.ImageGrid(pang_img, 1, 6)
        for i in death_anim:
            i = center_image(i)
        for i in pang_anim:
            i = center_image(i)

        self.anim = dict(
            mob1Qdeath=death_anim,
            pang01=pang_anim
        )

    def generateGridSettings(self):
        """ These control the grid that is the game window """
        w, h, gm, ssize = self.width, self.height, 0, 32
        self.squaresize = ssize
        self.grid_margin = gm
        self.grid_dim = (36, 21)
        self.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def updateGridSettings(self):
        w, h, gm, ssize = self.width, self.height, 0, 32
        self.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def generateGridIndicators(self):
        """ Generates the squares that indicates available blocks """
        w = self.squaresize
        points = []
        rects = []
        # self.batches["bg"] = pyglet.graphics.Batch()
        self.batches["bg2"] = pyglet.graphics.Batch()
        for p in self.grid.w_grid:
            wp = self.get_windowpos(p[0], p[1])
            x = wp[0] - w // 2
            y = wp[1] - w // 2
            points.append(wp[0])
            points.append(wp[1])
            r_points = [x, y, x + w, y, x + w, y + w, x, y + w]
            rects = rects + r_points
        # rect = self.batches["bg"].add(
        #     len(rects) / 2,
        #     GL_QUADS,
        #     self.bg_group,
        #     ('v2f', rects)
        #     )
        # dots = self.batches["bg2"].add(
        #     len(points) / 2,
        #     GL_POINTS,
        #     self.fg_group,
        #     ('v2f', (points))
        #     )

    ### Makes a list of points that represent lines of the grid path ###
    def generateGridPathIndicators(self):
        points = []
        i = 0
        s = self.get_windowpos(self.grid.start[0], self.grid.start[1])
        g0 = self.get_windowpos(self.grid.path[0][0], self.grid.path[0][1])
        points.append(s[0])
        points.append(s[1])
        points.append(g0[0])
        points.append(g0[1])
        for p in self.grid.path:
            if i < len(self.grid.path) - 1:
                points.append(self.get_windowpos(p[0], p[1])[0])
                points.append(self.get_windowpos(p[0], p[1])[1])
                pn = self.grid.path[i+1]
                points.append(self.get_windowpos(pn[0], pn[1])[0])
                points.append(self.get_windowpos(pn[0], pn[1])[1])
            i += 1

        return points, len(points) // 2

    def generateMobPathIndicators(self):
        points = []
        i_points = []
        s1 = set(self.grid.path)
        for m in self.mobs:
            s2 = set(m.path)
            if len(s2.difference(s1)) > 0:
                for p in s2.difference(s1):
                    points.append(p)

        if len(points) > 0:
            points = list(OrderedDict.fromkeys(points))
            for p in points:
                i_points.append(self.get_windowpos(p[0], p[1])[0])
                i_points.append(self.get_windowpos(p[0], p[1])[1])

        return i_points, len(i_points) / 2

    def get_windowpos(self, x, y):
        """Gets position of a grid coordinate on the window, in pixels"""
        gm, ss = self.grid_margin, self.squaresize
        ox, oy = self.offset_x, self.offset_y
        x = (ox + x * (ss + gm)) + ss / 2
        y = self.height - ((oy + y * (ss + gm)) + ss / 2)
        return (x, y)

    def place_tower(self, t, x, y, new=False):
        """Positions tower and updates game state accordingly."""
        placed = False
        grid = self.grid
        dist = self.height // 10  # Range to check for available square
        for g in grid.t_grid:
            if not g == grid.goal or g == grid.start:
                if x and y:
                    gx = self.get_windowpos(g[0], g[1])[0]
                    gy = self.get_windowpos(g[0], g[1])[1]
                    if get_dist(gx, gy, x, y) < dist:
                        dist = get_dist(gx, gy, x, y)
                        placed = False
                        if dist <= self.squaresize:
                            placed = True
                            new_g = g
                            new_rg = (gx, gy)

        if placed:
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
        print "SPAWNING"
        choice = random.randint(0, 2)
        if choice:
            mob = Mob(self, "YAY")
        else:
            mob = Mob1W(self, "YAY")

        self.mobs.append(mob)

    def pathFinding(self, dt, limit=1):
        if len(self.pf_queue) > 0:
            if self.debug:
                print("Calculating paths for pf_queue.")
            count = 0
            for m in self.pf_queue:
                if count == limit:
                    break
                m.updateTarget()
                self.pf_queue.remove(m)
                count += 1

    def span(self, dx, dy):
        self.offset_x += dx
        self.offset_y -= dy
        # self.updateGridSettings()
        self.bg.x += dx
        self.bg.y += dy

        # for w in self.walls:
        #     w.updatePos()

        for t in self.towers:
            t.updateOffset()

        for m in self.mobs:
            m.x += dx
            m.y += dy
            m.rx += dx
            m.ry += dy

        sx, sy = self.get_windowpos(self.grid.start[0], self.grid.start[1])
        for p in self.gas_emitter_group:
            p.position = sx, sy, 0

        gx, gy = self.get_windowpos(self.grid.goal[0], self.grid.goal[1])
        for p in self.flame_emitter_group:
            p.position = gx, gy, 0

        self.gas_emitter.template.position = sx, sy, 0
        self.flame_emitter.template.position = gx, gy, 0

        for p in self.puff_fx.group:
            p.position = (
                p.position[0] + dx,
                p.position[1] + dy,
                0
            )
        for p in self.smoke_fx.group:
            p.position = (
                p.position[0] + dx,
                p.position[1] + dy,
                0
            )
        for p in self.muzzle_fx.group:
            p.position = (
                p.position[0] + dx,
                p.position[1] + dy,
                0
            )

    def quit_game(self):
        print("Exiting...")
        pyglet.app.exit()

    ### EVENT HANDLERS ###
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.quit_game()
            # return True  # Disable ESC to exit
        elif symbol == key.SPACE:
            self.paused = not self.paused
            if self.paused:
                # Spawn main menu
                self.mainmenu = MainMenu(self)
                self.mainmenu.add_entry(title="Resume", action="resume")
                self.mainmenu.add_entry(title="New Game", action="newgame")
                self.mainmenu.add_entry(title="Exit", action="quit")
                pyglet.clock.unschedule(self.particle_system.update)
            else:
                self.mainmenu = None
                pyglet.clock.schedule_interval(
                    window.particle_system.update,
                    1.0/30.0
                )
        if not self.paused: # Only listen for these keys when game is running
            if symbol == key.Q:
                mob = Mob(self, "YAY")
                self.mobs.append(mob)
            elif symbol == key.W:
                mob = Mob1W(self, "YAY")
                self.mobs.append(mob)
            elif symbol == key.F11:
                self.set_fullscreen(not self.fullscreen)
                self.activate()
            elif symbol == key.F12:
                self.debug = not self.debug
            elif symbol == key._1:
                tower = Tower(self)
                self.selected_mouse = tower
            elif symbol == key._2:
                tower = SplashTower(self)
                self.selected_mouse = tower
            elif symbol == key._3:
                tower = PoisonTower(self)
                self.selected_mouse = tower
            elif symbol == key.LEFT:
                self.span(32, 0)
            elif symbol == key.RIGHT:
                self.span(-32, 0)
            elif symbol == key.UP:
                self.span(0, -32)
            elif symbol == key.DOWN:
                self.span(0, 32)
            elif symbol == key.F2:
                self.autospawn = not self.autospawn
                if self.autospawn:
                    pyglet.clock.schedule_interval(
                        self.autospawn_random,
                        1.0
                    )
                else:
                    pyglet.clock.unschedule(self.autospawn_random)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if not self.paused:
                # First, check if mouse is on a UI element
                t_type = self.userinterface.check_mouse((x, y))
                if t_type:  # check_mouse returns false if not on a button
                    if t_type == "1":
                        tower = Tower(self)
                        self.selected_mouse = tower
                    if t_type == "2":
                        tower = SplashTower(self)
                        self.selected_mouse = tower
                    if t_type == "3":
                        tower = PoisonTower(self)
                        self.selected_mouse = tower
                else:
                    if not self.selected_mouse:
                        for t in self.towers:

                            if x < t.x + t.size//2 and x > t.x - t.size//2:

                                if y < t.y + t.size//2 and y > t.y - t.size//2:
                                    self.selected_mouse = t
                                    self.towers.remove(t)
                                    self.grid.update()
                                    if t.gx and t.gy:
                                        self.grid.t_grid.append((t.gx, t.gy))
                                        self.grid.w_grid.append((t.gx, t.gy))
                                    break

                        if not self.selected_mouse:
                            tower = SplashTower(self, "Default", x=x, y=y)
                            self.place_tower(tower, x, y, new=True)

                    else:
                        self.place_tower(self.selected_mouse, x, y, new=True)
                        self.selected_mouse = None
            elif self.mainmenu:
                pos = (x, y)
                self.mainmenu.check_mouse(pos)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if self.selected_mouse:
                self.place_tower(self.selected_mouse, x, y, new=True)
                self.selected_mouse = None
                self.dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            if self.selected_mouse:
                self.dragging = True
                self.selected_mouse.updatePos(x, y, None, None)

        elif buttons & mouse.RIGHT:
            self.span(dx, dy)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.selected_mouse:
            self.selected_mouse.updatePos(x, y, None, None)
        self.cx, self.cy = x, y

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)
        self.activate()

        self.updateGridSettings()
        # self.generateGridIndicators()

        if not self.mainmenu:
            self.bg.x = self.offset_x
            self.bg.y = self.offset_y

        # for w in self.walls:
        #     w.updatePos()

            for t in self.towers:
                t.updateOffset()

            for m in self.mobs:
                m.updateOffset()

            sx, sy = self.get_windowpos(self.grid.start[0], self.grid.start[1])
            for p in self.gas_emitter_group:
                p.position = sx, sy, 0

            gx, gy = self.get_windowpos(self.grid.goal[0], self.grid.goal[1])
            for p in self.flame_emitter_group:
                p.position = gx, gy, 0

            self.gas_emitter.template.position = sx, sy, 0
            self.flame_emitter.template.position = gx, gy, 0

    def updateState(self):
        for t in self.towers:
            if not t.target:  # if tower has no target
                i = random.randrange(0, 3)
                for m in self.mobs:
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

    def setGL(self, state):
        if state == "on":
            for t in self.textures:
                glEnable(self.textures[t].texture.target)
        else:
            for t in self.textures:
                glDisable(self.textures[t].texture.target)

    def addParticleEmitters(self):
        self.flame_emitter_group = []
        self.gas_emitter_group = []
        sx = self.get_windowpos(self.grid.start[0], self.grid.start[1])[0]
        sy = self.get_windowpos(self.grid.start[0], self.grid.start[1])[1]
        gx = self.get_windowpos(self.grid.goal[0], self.grid.goal[1])[0]
        gy = self.get_windowpos(self.grid.goal[0], self.grid.goal[1])[1]
        w = self.squaresize
        
        color2 = (0.7,0.2,0.1,0.6)
        self.flame_emitter = StaticEmitter(
            rate=5,
            template=Particle(
                position=(gx, gy, 0), 
                color=color2), 
            deviation=Particle(
                position=(1, 1, 0),
                velocity=(0.6, 0.2, 0),
                color=(0,0.02,0,0),
                age=1))
        self.flame_emitter_group = ParticleGroup(
            controllers=[self.flame_emitter, Lifetime(6),
                Gravity((-1.5,0,0)), Movement(),
                Fader(
                    fade_in_start=0, start_alpha=0,
                    fade_in_end=0.20, max_alpha=0.5,
                    fade_out_start=2.0, fade_out_end=5.0
                )
            ],
            system=self.particle_system,
            renderer=PointRenderer(32, SpriteTexturizer(
                self.effects["smoke"].texture.id)
            )
        )

        color = (0,0.5,0.7,0.6)
        self.gas_emitter = StaticEmitter(
            rate=5,
            template=Particle(
                position=(sx, sy, 0), 
                color=color), 
            deviation=Particle(
                position=(1, 1, 0),
                velocity=(0.6, 0.2, 0),
                color=(0,0.03,0,0),
                age=1))
        self.gas_emitter_group = ParticleGroup(
            controllers=[self.gas_emitter, Lifetime(6),
                Gravity((1.5,0,0)), Movement(),
                Fader(
                    fade_in_start=0, start_alpha=0, fade_in_end=0.20, max_alpha=0.5, 
                    fade_out_start=2.0, fade_out_end=5.0
                )
            ],
            system=self.particle_system,
            renderer=PointRenderer(32, SpriteTexturizer(
                self.effects["smoke"].texture.id)
            )
        )

    def render(self, dt):
        """ Rendering method, need to remove game logic """
        if not self.paused and not self.mainmenu:
            # Initialize Projection matrix
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()

            glMatrixMode(GL_MODELVIEW)
            # # Initialize Modelview matrix
            glLoadIdentity()
            # # Save the default modelview matrix
            # glPushMatrix()
            glClear(GL_COLOR_BUFFER_BIT)

            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_LINE_SMOOTH)
            glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)

            # glOrtho(50, self.width - 50, 50, self.height - 50, 1, -1)
            glOrtho(0, self.width, 0, self.height, 1, -1)

            glColor4f(0, 0, 0, 1)

            # glColor4f(1, 1, 1, 0.2)

            glColor4f(0.3, 0.3, 0.3, 1.0)
            glPointSize(3)
            self.setGL("on")
            glColor4f(1, 1, 1, 1)
            self.batches["bg"].draw()
            self.batches["mobs"].draw()
            # if self.debug:
            #     self.batches["walls"].draw()
            self.batches["towers"].draw()
            self.batches["anim"].draw()
            
            ### Draw UI ###
            self.userinterface.render()

            self.setGL("off")

            glShadeModel(GL_SMOOTH)
            glEnable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)
            self.particle_system.draw()

            if self.debug:
                glLineWidth(3)
                points, count = self.generateGridPathIndicators()
                glColor4f(0.4, 0.4, 0.8, 0.7)
                pyglet.graphics.draw(
                    count,
                    GL_LINES,
                    ('v2f', points)
                )

                points, count = self.generateMobPathIndicators()
                glColor4f(0.7, 0.5, 0.3, 1.0)
                pyglet.graphics.draw(
                    count,
                    GL_POINTS,
                    ('v2f', points)
                )

            # for p in self.grid.w_grid:

            #     glColor4f(1, 0, 1, 1)
            #     x, y = self.get_windowpos(p[0], p[1])
            #     pyglet.graphics.draw(
            #         1,
            #         GL_POINTS,
            #         ('v2f', (x, y))
            #         )
            ### Draw mob health bars ###
            glColor4f(0.6, 0.3, 0.3, 1.0)
            glLineWidth(3)
            for m in self.mobs:
                # glColor4f(0.6, 0.3, 0.3, 0.2 + (m.hp / 100.0) * 0.8)
                if m.hp < m.hp_max:
                    pyglet.graphics.draw(
                        2,
                        GL_LINES,
                        (
                            'v2f',
                            (
                                m.x - 1 - int((m.hp / m.hp_max) * 8),
                                m.y + 10,
                                m.x - 1 + int((m.hp / m.hp_max) * 8),
                                m.y + 10)
                            )
                        )

            ### Update animations ###
            for a in self.animations:
                a.update()
                if not a.playing:
                    self.animations.remove(a)

            if self.debug:
                fps_display.draw()

            self.updateState()

        else:
            self.mainmenu.render()

if __name__ == "__main__":
    window = Game()
    pyglet.clock.schedule_interval(window.render, 1.0/60.0)
    pyglet.app.run()

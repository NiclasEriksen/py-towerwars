import pyglet
import math
from random import gauss, uniform
from collections import OrderedDict
from pyglet.window import key, mouse
from pyglet import image
from pyglet.gl import *
from lepton import Particle, ParticleGroup, default_system
from lepton.emitter import StaticEmitter
from lepton.renderer import PointRenderer
from lepton.texturizer import SpriteTexturizer, create_point_texture
from lepton.controller import Gravity, Lifetime, Movement, Fader, ColorBlender, Growth

from functions import *
from grid import *


### Global variables ###
DEBUG = False
RES_PATH = "../resources/"
SCREENRES = (1280, 720)  # The resolution for the game window
VSYNC = True
SCREEN_MARGIN = 15  # %
WALLGRID = [
    (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (5, 6), (6, 6), (7, 6),
    (8, 6), (9, 6), (10, 6), (11, 6), (11, 7), (11, 8), (11, 9), (12, 9),
    (13, 9), (14, 9), (15, 9), (16, 9), (17, 9), (18, 9), (18, 10), (18, 11),
    (18, 12), (19, 12), (20, 12)
]

### Get information about the OS and display ###
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

### Limit the frames per second to 60 ###
pyglet.clock.set_fps_limit(60)
fps_display = pyglet.clock.ClockDisplay()

n_particle = Particle(
    velocity=(0,0,0), 
    color=(0.85 ,0.40, 0.25, 0.7)
)

############################
### Import classes ###
from tower import *
from mob import *
from wall import *
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
        self.cx, self.cy = 0, 0  # Cursor position
        glClearColor(0.1, 0.1, 0.1, 1)  # Background color
        self.particle_system = default_system

        self.batches = OrderedDict()
        self.batches["fg"] = pyglet.graphics.Batch()
        self.batches["mobs"] = pyglet.graphics.Batch()
        self.batches["bg"] = pyglet.graphics.Batch()
        self.batches["bg2"] = pyglet.graphics.Batch()
        self.batches["walls"] = pyglet.graphics.Batch()
        self.batches["anim"] = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        self.fg_group = pyglet.graphics.OrderedGroup(1)

        self.loadTextures()

        ### Particle group ###
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        self.puff_fx = ParticleCategory(self, "simple", "puff")
        self.smoke_fx = ParticleCategory(self, "simple", "smoke")
        self.muzzle_fx = ParticleCategory(self, "simple", "pang")
        ### Generates grid parameters for game instance ###
        self.generateGridSettings()
        self.grid = Grid(self)

        ### Lists of game objects ###
        self.mobs = []  # Enemy mob sprite objects
        self.mob_count = 0  # This serve as mob's id
        self.towers = []  # Tower sprite objects
        self.walls = []  # Wall sprite objects
        self.placeWalls()  # Fills walls list and updates grid
        self.animations = []
        self.selected = None
        self.dragging = False
        self.highlighted = []

        ### Pathfinding stuff ###
        self.pf_queue = []
        self.pf_clusters = []

        self.addParticleEmitters()
        self.generateGridIndicators()

    def loadTextures(self):

        ### Get images from resource cache and centers their anchor points ###
        ws_img = center_image(pyglet.image.load(RES_PATH + 'wall_stone.png'))
        tw_img = center_image(pyglet.image.load(RES_PATH + 'tower_wood.png'))
        p_texture = pyglet.image.load(RES_PATH + 'particle.png')
        p_smoke_texture = pyglet.image.load(RES_PATH + 'particle_smoke.png')
        p_pang_texture = pyglet.image.load(RES_PATH + 'particle_pang.png')
        tp_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_poison.png')
        )
        ts_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_splash.png')
        )
        ts_t_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_splash_turret.png')
        )
        tb_img = center_image(pyglet.image.load(RES_PATH + 'tower_blue.png'))
        mob_1w = center_image(pyglet.image.load(RES_PATH + 'mob_1w.png'))
        mob_1q = center_image(pyglet.image.load(RES_PATH + 'mob.png'))


        self.textures = dict(
            wall_stone=ws_img,
            tower_wood=tw_img,
            tower_poison=tp_img,
            tower_splash=ts_img,
            tower_splash_turret=ts_t_img,
            mob1Q=mob_1q,
            mob1W=mob_1w
        )

        self.effects = dict(
            puff=p_texture,
            smoke=p_smoke_texture,
            pang=p_pang_texture
        )
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
        w, h, gm, ssize = self.width, self.height, 1, 32
        self.squaresize = ssize
        self.grid_margin = gm
        self.grid_dim = (32, 20)
        self.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def generateGridIndicators(self):
        """ Generates the squares that indicates available blocks """
        w = self.squaresize
        points = []
        rects = []
        self.batches["bg"] = pyglet.graphics.Batch()
        self.batches["bg2"] = pyglet.graphics.Batch()
        for p in self.grid.grid:
            wp = self.get_windowpos(p[0], p[1])
            x = wp[0] - w // 2
            y = wp[1] - w // 2
            points.append(wp[0])
            points.append(wp[1])
            r_points = [x, y, x + w, y, x + w, y + w, x, y + w]
            rects = rects + r_points

            # rect = self.batches["bg"].add(
            #     4,
            #     GL_QUADS,
            #     self.bg_group,
            #     ('v2f', (x, y,
            #              x + w, y,
            #              x + w, y + w,
            #              x, y + w))
            #     )

        rect = self.batches["bg"].add(
            len(rects) / 2,
            GL_QUADS,
            self.bg_group,
            ('v2f', rects)
            )

        dots = self.batches["bg2"].add(
            len(points) / 2,
            GL_POINTS,
            self.fg_group,
            ('v2f', (points))
            )

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
        i = 0
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


    def placeWalls(self):
        for g in WALLGRID:
            wall = Wall(self, g[0], g[1])
            self.walls.append(wall)
        self.grid.update()

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
        for g in grid.grid:
            if not g == grid.goal or g == grid.start:
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


            update = False
            if new_g in grid.path:
                update = True
            else:
                for p in grid.path:
                    if new_g in get_diagonal(
                        grid.grid,
                        p[0], p[1]
                    ):
                        update = True
                        break
                    elif new_g in get_neighbors(
                        grid.grid,
                        p[0], p[1]
                    ):
                        update = True
                        break

            if update:
                for m in self.mobs:
                    if m not in self.pf_queue:
                        if check_path(m, grid.grid, new_g):
                            self.pf_queue.append(m)

            grid.update(new=update)
            # self.pathFinding(limit=100)

            if self.debug:
                print("New path for grid: {0}".format(update))

            if self.debug:
                print("Tower placed at [{0},{1}]".format(new_g[0], new_g[1]))

    def pathFinding(self, dt, limit=1):
                #!/usr/bin/python

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

    ### EVENT HANDLERS ###
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            print("Exiting...")
            pyglet.app.exit()
            # return True  # Disable ESC to exit
        elif symbol == key.Q:
            mob = Mob(self, "YAY")
            self.mobs.append(mob)
        elif symbol == key.W:
            mob = Mob1W(self, "YAY")
            self.mobs.append(mob)
        elif symbol == key.F11:
            self.set_fullscreen(not self.fullscreen)
        elif symbol == key.F1:
            self.grid.exportGrid()
        elif symbol == key.F2:
            print(importGrid(self))
        elif symbol == key.F3:
            self.generateMobPathIndicators()
        elif symbol == key.F12:
            self.debug = not self.debug
        elif symbol == key._1:
            tower = Tower(self)
            self.selected = tower
        elif symbol == key._2:
            tower = SplashTower(self)
            self.selected = tower
        elif symbol == key._3:
            tower = PoisonTower(self)
            self.selected = tower
        elif symbol == key.F:
            anim = animation.Animation(
                self, self.anim["pang01"], 50, 50
            )

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if not self.selected:
                for t in self.towers:

                    if x < t.x + t.size//2 and x > t.x - t.size//2:

                        if y < t.y + t.size//2 and y > t.y - t.size//2:
                            self.selected = t
                            self.grid.update()
                            self.grid.grid.append((t.gx, t.gy))
                            break

                if not self.selected:
                    tower = SplashTower(self, "Default", x=x, y=y)
                    self.place_tower(tower, x, y, new=True)

            else:
                self.place_tower(self.selected, x, y, new=True)
                self.selected = None

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if self.selected:
                if self.dragging:
                    self.place_tower(self.selected, x, y)
                    self.selected = None
                    self.dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            if self.selected:
                self.dragging = True
                self.selected.updatePos(x, y, None, None)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.selected:
            self.selected.updatePos(x, y, None, None)
        self.cx, self.cy = x, y

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

        self.generateGridSettings()
        self.generateGridIndicators()

        for w in self.walls:
            w.updatePos()

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
        sx = self.get_windowpos(self.grid.start[0], self.grid.start[1])[0]
        sy = self.get_windowpos(self.grid.start[0], self.grid.start[1])[1]
        gx = self.get_windowpos(self.grid.goal[0], self.grid.goal[1])[0]
        gy = self.get_windowpos(self.grid.goal[0], self.grid.goal[1])[1]
        w = self.squaresize
        #     template=n_particle,
        #     color=(0.8,0.4,0.2,0.8),
        #     rate=20,
        #     position=(g[0], g[1], 0),
        #     deviation=Particle(position=(0,0,0), velocity=(1,1,0), age=1)
        # )
        # emitter = particles.ParticleCategory(
        #     self, "emitter", "smoke",
        #     x=gx, y=gy, color=(1,0.3,0.3,0.5)
        # )
        
        color2 = (0.8,0.2,0.7,0.5)
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

        color = (0.2,0.8,1,0.5)
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
        glClear(GL_COLOR_BUFFER_BIT)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)

        glColor4f(0.12, 0.12, 0.12, 1.0)
        self.batches["bg"].draw()

        glColor4f(0.3, 0.3, 0.3, 1.0)
        glPointSize(1)
        self.batches["bg2"].draw()

        self.batches["fg"].draw()
        ## Draw turrets ###
        # for t in self.towers:
        #     r, g, b = t.turret_color[0], t.turret_color[1], t.turret_color[2]
        #     a = 1.0
        #     glLineWidth(t.turret_width)
        #     glColor4f(r, g, b, a)
        #     x = t.x + t.turret_size * math.cos(math.radians(t.angle))
        #     y = t.y + t.turret_size * math.sin(math.radians(t.angle))
        #     pyglet.graphics.draw(
        #         2,
        #         GL_LINES,
        #         ('v2f', (t.x, t.y, x, y))
        #         )
        self.setGL("on")
        self.batches["mobs"].draw()
        self.batches["walls"].draw()
        self.batches["anim"].draw()
        self.setGL("off")

        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        self.particle_system.draw()

        if self.debug:
            glLineWidth(3)
            points, count = self.generateGridPathIndicators()
            glColor4f(0.5, 0.7, 0.4, 0.3)
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


if __name__ == "__main__":
    window = Game()
    pyglet.clock.schedule_interval(window.render, 1.0/60.0)
    window.particle_system.run_ahead(2.0, 30.0)
    pyglet.clock.schedule_interval(window.particle_system.update, 1.0/30.0)
    pyglet.clock.schedule_interval(window.pathFinding, 1.0/20.0)
    pyglet.app.run()

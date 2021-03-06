#!/bin/python2
import pyglet   # Version 1.2.2
# from audio import AudioFile  # Sound engine
from math import pi, sin, cos
from collections import OrderedDict
from pyglet.window import key, mouse
from pyglet.gl import *
from lepton import Particle, ParticleGroup, default_system
from lepton.emitter import StaticEmitter
from lepton.renderer import PointRenderer
from lepton.texturizer import SpriteTexturizer
from lepton.controller import (
    Gravity, Lifetime, Movement, Fader
)
############################
# Import classes #
from game import *
from tower import *
from mob import *
from ui import *
import pypf
from animation import *
from particles import *
from functions import *

# Sound engine
pyglet.options['audio'] = ('openal', 'pulse', 'silent')

# Global variables #
DEBUG = False
RES_PATH = "resources/"
SCREENRES = (1440, 900)  # The resolution for the game window
VSYNC = True
PAUSED = False
SCREEN_MARGIN = 15  # %
FPS = 30.0

# Get information about the OS and display #
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

# Limit the frames per second to 60 #
pyglet.clock.set_fps_limit(FPS)
fps_display = pyglet.clock.ClockDisplay()


class GameWindow(pyglet.window.Window):  # Main game window

    def __init__(self):
        # Template for multisampling
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
        # Create OpenGL context #
        gl_context = gl_config.create_context(None)
        super(GameWindow, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=True,
            vsync=VSYNC
            )
        # GL and graphics variables #
        self.width = SCREENRES[0]
        self.height = SCREENRES[1]
        self.offset = (0, 0)
        self.fps = FPS
        self.cx, self.cy = 0, 0  # Cursor position
        glClearColor(0.1, 0.1, 0.1, 1)  # Background color
        self.particle_system = default_system
        self.tile_renderer = None
        self.loading = False

        self.batches = OrderedDict()
        self.batches["mobs"] = pyglet.graphics.Batch()
        self.batches["flying_mobs"] = pyglet.graphics.Batch()
        self.batches["bg1"] = pyglet.graphics.Batch()
        self.batches["obs"] = pyglet.graphics.Batch()
        self.batches["fg"] = pyglet.graphics.Batch()
        self.batches["fg2"] = pyglet.graphics.Batch()
        self.batches["bg2"] = pyglet.graphics.Batch()
        self.batches["towers"] = pyglet.graphics.Batch()
        self.batches["buttons"] = pyglet.graphics.Batch()
        self.batches["mm_buttons"] = pyglet.graphics.Batch()
        # self.batches["walls"] = pyglet.graphics.Batch()
        self.batches["anim"] = pyglet.graphics.Batch()
        self.ui_group = pyglet.graphics.OrderedGroup(2)
        self.fg_group = pyglet.graphics.OrderedGroup(1)

        self.loadFonts()    # Loads fonts into memory
        self.currently_playing = []
        self.sound_enabled = True
        self.loadSFX()      # Load sound files into memory
        self.loadTextures()

        # GL modes #
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)

        # Lists of game objects #
        self.animations = []

        # self.generateGridSettings()
        self.game = Game(self)

        print("Creating UI")
        self.userinterface = UI(self)

        # Spawn main menu
        self.mainmenu = MainMenu(self)
        self.mainmenu.add_entry(title="New Game", action="newgame")
        self.mainmenu.add_entry(title="Exit", action="quit")

        # Start a new game
        # self.newGame()

    def flushWindow(self):
        try:
            if self.debug:
                print("Removing old particle system.")
            self.particle_system.remove_group(self.flame_emitter_group)
            self.particle_system.remove_group(self.gas_emitter_group)
        except AttributeError:
            pass
        try:
            pyglet.clock.unschedule(self.particle_system.update)
        except AttributeError:
            pass
        self.particle_system = default_system
        self.particle_system.run_ahead(2.0, 30.0)
        pyglet.clock.schedule_interval(self.particle_system.update, 1.0/30.0)

        self.batches = OrderedDict()
        self.batches["mobs"] = pyglet.graphics.Batch()
        self.batches["flying_mobs"] = pyglet.graphics.Batch()
        self.batches["bg1"] = pyglet.graphics.Batch()
        self.batches["bg2"] = pyglet.graphics.Batch()
        self.batches["obs"] = pyglet.graphics.Batch()
        self.batches["fg"] = pyglet.graphics.Batch()
        self.batches["fg2"] = pyglet.graphics.Batch()
        self.batches["towers"] = pyglet.graphics.Batch()
        self.batches["buttons"] = pyglet.graphics.Batch()
        self.batches["mm_buttons"] = pyglet.graphics.Batch()
        self.batches["anim"] = pyglet.graphics.Batch()
        self.ui_group = pyglet.graphics.OrderedGroup(2)
        self.fg_group = pyglet.graphics.OrderedGroup(1)

        # Particles and stuff
        self.puff_fx = None
        self.smoke_fx = None
        self.muzzle_fx = None
        self.skull_fx = None
        self.crit_fx = None

        self.puff_fx = ParticleCategory(self, "simple", "puff")
        self.smoke_fx = ParticleCategory(self, "simple", "smoke")
        self.muzzle_fx = ParticleCategory(self, "simple", "pang")
        self.skull_fx = ParticleCategory(self, "simple", "skull")
        self.crit_fx = ParticleCategory(self, "simple", "crit")
        self.blood_fx = ParticleCategory(self, "simple", "blood")
        self.particlestest = (
            self.puff_fx,
            self.smoke_fx,
            self.muzzle_fx,
            self.skull_fx,
            self.crit_fx
        )
        self.flame_emitter, self.gas_emitter = None, None

    def loadFonts(self):
        pyglet.font.add_file(RES_PATH + 'soft_elegance.ttf')
        pyglet.font.add_file(RES_PATH + 'ui/' + 'visitor1.ttf')
        self.ui_font = pyglet.font.load('Soft Elegance')
        self.small_font = pyglet.font.load('Visitor TT1 BRK')

    def loadTextures(self):
        ws_img = center_image(pyglet.image.load(RES_PATH + 'wall_stone.png'))
        tw_img = center_image(pyglet.image.load(RES_PATH + 'tower_wood.png'))
        p_texture = pyglet.image.load(RES_PATH + 'particle.png')
        p_smoke_texture = pyglet.image.load(RES_PATH + 'particle_smoke.png')
        p_pang_texture = pyglet.image.load(RES_PATH + 'particle_pang.png')
        p_skull_texture = pyglet.image.load(RES_PATH + 'particle_skull.png')
        p_crit_texture = pyglet.image.load(RES_PATH + 'crit.png')
        p_blood_texture = pyglet.image.load(RES_PATH + 'blood.png')
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
        tc_img = center_image(pyglet.image.load(
            RES_PATH + 'tower_chain.png')
        )
        mob_1q = center_image(pyglet.image.load(RES_PATH + 'mob.png'))
        mob_1w = center_image(pyglet.image.load(RES_PATH + 'mob_1w.png'))
        mob_1e = center_image(pyglet.image.load(RES_PATH + 'mob_1e.png'))
        mob_1r = center_image(pyglet.image.load(RES_PATH + 'mob_1r.png'))
        mob_1a = center_image(pyglet.image.load(RES_PATH + 'mob_1a.png'))
        mob_1s = center_image(pyglet.image.load(RES_PATH + 'mob_1s.png'))
        mob_1d = center_image(pyglet.image.load(RES_PATH + 'mob_1d.png'))
        mob_1f = center_image(pyglet.image.load(RES_PATH + 'mob_1f.png'))
        mob_1z = center_image(pyglet.image.load(RES_PATH + 'mob_1z.png'))
        # bg01 = pyglet.image.load(RES_PATH + 'bg01.png')

        self.textures = dict(
            wall_stone=ws_img,
            tower_wood=tw_img,
            tower_poison=tp_img,
            tower_poison_turret=tp_t_img,
            tower_splash=ts_img,
            tower_splash_turret=ts_t_img,
            tower_chain=tc_img,
            mob1Q=mob_1q,
            mob1W=mob_1w,
            mob1E=mob_1e,
            mob1R=mob_1r,
            mob1A=mob_1a,
            mob1S=mob_1s,
            mob1D=mob_1d,
            mob1F=mob_1f,
            mob1Z=mob_1z,
        )

        self.effects = dict(
            puff=p_texture,
            smoke=p_smoke_texture,
            skull=p_skull_texture,
            pang=p_pang_texture,
            crit=p_crit_texture,
            blood=p_blood_texture,
        )

        # Load images and create image grids for animations #
        # and centers their frame anchor point              #
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

    def loadSFX(self):
        # impact1 = AudioFile(RES_PATH + "impact1.wav")
        impact1 = pyglet.media.load(RES_PATH + "impact1.ogg", streaming=False)
        impact2 = pyglet.media.load(RES_PATH + "impact2.ogg", streaming=False)
        dart = pyglet.media.load(RES_PATH + "dart.ogg", streaming=False)
        bang1 = pyglet.media.load(RES_PATH + "bang1.ogg", streaming=False)
        bang2 = pyglet.media.load(RES_PATH + "bang2.ogg", streaming=False)
        pluck = pyglet.media.load(RES_PATH + "pluck.ogg", streaming=False)
        # impact1.play()
        # tkSnack.audio.play()
        self.sfx = dict(
            impact1=impact1,
            impact2=impact2,
            dart=dart,
            bang1=bang1,
            bang2=bang2,
            pluck=pluck
        )

    def play_sfx(self, sound="default", volume=1.0):
        if self.sound_enabled:
            for s in self.currently_playing:
                if s.time == 0.0:
                    self.currently_playing.remove(s)

            if len(self.currently_playing) < 5:
                playing = self.sfx[sound].play()
                playing.volume = volume
                self.currently_playing.append(playing)

        # try:
        #     print self.sfx[sound].duration
        #     print playing.time
        # except:
        #     print("Unable to play sound {0}".format(sound))

    def generateGridSettings(self):
        """ These control the grid that is the game window """
        w, h, gm, ssize = self.width, self.height, 0, 32
        self.squaresize = ssize
        self.grid_margin = gm
        self.grid_dim = (36, 21)
        self.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    # def updateGridSettings(self):
    #     w, h, gm, ssize = self.width, self.height, 0, 32
    #     self.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
    #     self.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def generateGridIndicators(self):
        """ Generates the squares that indicates available blocks """
        w = self.squaresize
        points = []
        rects = []
        for p in self.grid.w_grid:
            wp = self.get_windowpos(p[0], p[1])
            x = wp[0] - w // 2
            y = wp[1] - w // 2
            points.append(wp[0])
            points.append(wp[1])
            r_points = [x, y, x + w, y, x + w, y + w, x, y + w]
            rects = rects + r_points

    def generateGridPathIndicators(self):
        # Makes a list of points that represent lines of the grid path #
        points = []
        i = 0
        g = self.game.grid
        s = self.get_windowpos(g.start[0], g.start[1])
        g0 = self.get_windowpos(g.path[0][0], g.path[0][1])
        points.append(s[0])
        points.append(s[1])
        points.append(g0[0])
        points.append(g0[1])
        for p in g.path:
            if i < len(g.path) - 1:
                points.append(self.get_windowpos(p[0], p[1])[0])
                points.append(self.get_windowpos(p[0], p[1])[1])
                pn = g.path[i+1]
                points.append(self.get_windowpos(pn[0], pn[1])[0])
                points.append(self.get_windowpos(pn[0], pn[1])[1])
            i += 1

        return points, len(points) // 2

    def generateMobPathIndicators(self):
        points = []
        i_points = []
        s1 = set(self.game.grid.path)
        for m in self.game.mobs:
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
        gm, ss = self.game.grid_margin, self.game.squaresize
        ox, oy = self.offset_x, self.offset_y
        x = (ox + x * (ss + gm)) + ss / 2
        y = self.height - ((oy + y * (ss + gm)) + ss / 2)
        return (x, y)

    def span(self, dx, dy):
        self.offset_x += dx
        self.offset_y -= dy

        for t in self.game.towers:
            t.updateOffset()

        for m in self.game.mobs:
            m.x += dx
            m.y += dy
            m.rx += dx
            m.ry += dy

        for t in self.tile_renderer.sprites:
            t.x += dx
            t.y += dy

        grid = self.game.grid

        sx, sy = self.get_windowpos(grid.start[0], grid.start[1])
        for p in self.gas_emitter_group:
            p.position = sx, sy, 0

        gx, gy = self.get_windowpos(grid.goal[0], grid.goal[1])
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

    def pause_game(self, state):
        self.game.paused = state
        if state:
            # Spawn main menu
            self.mainmenu = MainMenu(self)
            if self.game.loaded:
                self.mainmenu.add_entry(title="Resume", action="resume")
            self.mainmenu.add_entry(title="New Game", action="newgame")
            self.mainmenu.add_entry(title="Exit", action="quit")
            pyglet.clock.unschedule(self.particle_system.update)
        else:
            self.mainmenu = None
            pyglet.clock.schedule_interval(
                self.particle_system.update,
                1.0/30.0
            )

    def load_screen(self):
        print("Loadscreen")
        label = pyglet.text.Label(
                "Loading...", font_name='Soft Elegance',
                font_size=18,
                x=self.width // 2, y=self.height // 2,
                anchor_x="center", anchor_y="center",
                color=(255, 255, 255, 255)
            )

        glColor4f(0.4, 0.4, 0.3, 0.7)
        self.draw_circle(
            self.width // 2, self.height // 2, 70
        )

        label.draw()

    def quit_game(self):
        print("Exiting...")
        pyglet.app.exit()

    # EVENT HANDLERS #
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            if self.game.loaded:
                self.pause_game(not self.game.paused)
            else:
                self.quit_game()
            # return True  # Disable ESC to exit
        elif symbol == key.SPACE:
            if self.game.loaded:
                self.pause_game(not self.game.paused)
        if not self.game.paused:  # Only listen for keys if game is running
            if symbol == key.Q:
                mob = Mob(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.W:
                mob = Mob1W(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.E:
                mob = Mob1E(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.R:
                mob = Mob1R(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.A:
                mob = Mob1A(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.S:
                mob = Mob1S(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.D:
                mob = Mob1D(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.F:
                mob = Mob1F(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.Z:
                mob = Mob1Z(self.game, "YAY")
                self.game.mobs.append(mob)
            elif symbol == key.F11:
                self.set_fullscreen(not self.fullscreen)
                self.activate()
            elif symbol == key.F12:
                self.game.debug = not self.game.debug
                self.debug = self.game.debug
            elif symbol == key.G and self.debug:
                self.game.gold += 100
            elif symbol == key.F5:
                self.sound_enabled = not self.sound_enabled
            elif symbol == key.LEFT:
                self.span(32, 0)
            elif symbol == key.RIGHT:
                self.span(-32, 0)
            elif symbol == key.UP:
                self.span(0, -32)
            elif symbol == key.DOWN:
                self.span(0, 32)
            elif symbol == key.F2:
                self.game.autospawn = not self.game.autospawn
                if self.game.autospawn:
                    pyglet.clock.schedule_interval(
                        self.game.autospawn_random,
                        1.0
                    )
                else:
                    pyglet.clock.unschedule(self.game.autospawn_random)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if not self.game.paused:
                # First, check if mouse is on a UI element
                if self.userinterface.check_mouse((x, y)):  # returns false if
                    pass                                    # not on a button
                else:
                    if not self.game.mouse_drag_tower:
                        for t in self.game.towers:
                            # Checks for towers under cursor
                            if x < t.x + t.size//2 and x > t.x - t.size//2:

                                if y < t.y + t.size//2 and y > t.y - t.size//2:
                                    # Binds tower to mouse and removes tower
                                    self.game.selected_mouse = t
                                    break

                        if self.debug:
                            if not self.game.selected_mouse:
                                tower = SplashTower(
                                    self.game, "Default", x=x, y=y
                                )
                                self.game.place_tower(tower, x, y, new=True)

                    else:
                        self.game.place_tower(
                            self.game.mouse_drag_tower, x, y, new=True
                        )
                        self.game.mouse_drag_tower = None
            elif self.mainmenu:
                pos = (x, y)
                self.mainmenu.check_mouse(pos)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            # First, check if mouse is released over a UI element
            t_type = self.userinterface.check_mouse((x, y))
            if t_type:  # check_mouse returns false if not on a button
                if t_type == "1":
                    tower = Tower(self.game)
                    self.game.mouse_drag_tower = tower
                    self.game.active_tower = self.game.mouse_drag_tower
                elif t_type == "2":
                    tower = PoisonTower(self.game)
                    self.game.mouse_drag_tower = tower
                    self.game.active_tower = self.game.mouse_drag_tower
                elif t_type == "3":
                    tower = SplashTower(self.game)
                    self.game.mouse_drag_tower = tower
                    self.game.active_tower = self.game.mouse_drag_tower
                elif t_type == "4":
                    tower = ChainTower(self.game)
                    self.game.mouse_drag_tower = tower
                    self.game.active_tower = self.game.mouse_drag_tower
                elif t_type == "sell":
                    # Sell active tower!
                    self.game.gold += int(self.game.active_tower.price * 0.75)
                    self.game.towers.remove(self.game.active_tower)
                    self.game.active_tower = None
                    self.game.grid.update()
                elif t_type == "upgrade":
                    if self.game.active_tower:
                        self.game.active_tower.upgrade()

            elif self.game.mouse_drag_tower:
                self.game.active_tower = self.game.mouse_drag_tower
                self.game.place_tower(
                    self.game.mouse_drag_tower, x, y, new=True
                )
                self.game.selected_mouse = None
                self.game.mouse_drag_tower = None
                self.game.dragging = False
            elif self.game.selected_mouse:
                t = self.game.selected_mouse
                self.game.active_tower = t
                self.game.selected_mouse = None
                self.game.dragging = False
            elif not self.game.active_tower and self.game.dragging:
                self.game.active_tower = None
                self.game.dragging = None

            else:
                self.game.active_tower = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.game.dragging = True
            if self.game.selected_mouse and self.debug:
                if self.game.selected_mouse in self.game.towers:
                    t = self.game.selected_mouse
                    self.game.gold += t.price
                    self.game.towers.remove(t)
                    g = self.game.grid
                    g.update()
                    if t.gx and t.gy:
                        g.t_grid.append((t.gx, t.gy))
                        g.w_grid.append((t.gx, t.gy))

                self.game.mouse_drag_tower = self.game.selected_mouse
                self.game.selected_mouse.updatePos(x, y, None, None)
            else:
                t_type = self.userinterface.check_mouse((x, y))
                if self.game.mouse_drag_tower:
                    self.game.mouse_drag_tower.updatePos(x, y, None, None)
                # First, check if mouse is released over a UI element
                elif t_type:  # check_mouse returns false if not on a button
                    if t_type == "1":
                        tower = Tower(self.game)
                        self.game.mouse_drag_tower = tower
                    if t_type == "2":
                        tower = PoisonTower(self.game)
                        self.game.mouse_drag_tower = tower
                    if t_type == "3":
                        tower = SplashTower(self.game)
                        self.game.mouse_drag_tower = tower
                    if t_type == "4":
                        tower = ChainTower(self.game)
                        self.game.mouse_drag_tower = tower
                    self.game.selected_mouse = self.game.mouse_drag_tower
                elif self.game.active_tower:
                    t = self.game.active_tower
                    if (
                        (x <= t.x - t.size//2) or
                        (x >= t.x + t.size//2) or
                        (y <= t.y - t.size//2) or
                        (y >= t.y + t.size//2)
                    ):
                        for t in self.game.towers:
                            # Checks for towers under cursor
                            if x < t.x + t.size//2 and x > t.x - t.size//2:

                                if y < t.y + t.size//2 and y > t.y - t.size//2:
                                    # Binds tower to mouse and removes tower
                                    mdt = t
                                    self.game.selected_mouse = mdt
                                    self.game.active_tower = mdt
                                    break

            if not self.game.selected_mouse:
                self.game.active_tower = None

        elif buttons & mouse.RIGHT:
            self.span(dx, dy)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game.mouse_drag_tower:
            self.game.mouse_drag_tower.updatePos(x, y, None, None)
        self.cx, self.cy = x, y

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)
        self.activate()

        if not self.mainmenu:
            self.game.updateGridSettings()

            for t in self.game.towers:
                t.updateOffset()

            for m in self.game.mobs:
                m.updateOffset()

            self.userinterface.update_offset()

            self.tile_renderer.update_offset()

            grid = self.game.grid
            sx, sy = self.get_windowpos(grid.start[0], grid.start[1])
            for p in self.gas_emitter_group:
                p.position = sx, sy, 0

            gx, gy = self.get_windowpos(grid.goal[0], grid.goal[1])
            for p in self.flame_emitter_group:
                p.position = gx, gy, 0

            self.gas_emitter.template.position = sx, sy, 0
            self.flame_emitter.template.position = gx, gy, 0

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
        grid = self.game.grid
        sx = self.get_windowpos(grid.start[0], grid.start[1])[0]
        sy = self.get_windowpos(grid.start[0], grid.start[1])[1]
        gx = self.get_windowpos(grid.goal[0], grid.goal[1])[0]
        gy = self.get_windowpos(grid.goal[0], grid.goal[1])[1]

        color2 = (0.7, 0.2, 0.1, 0.6)
        self.flame_emitter = StaticEmitter(
            rate=5,
            template=Particle(
                position=(gx, gy, 0),
                color=color2),
            deviation=Particle(
                position=(1, 1, 0),
                velocity=(0.6, 0.2, 0),
                color=(0, 0.02, 0, 0),
                age=1))
        self.flame_emitter_group = ParticleGroup(
            controllers=[self.flame_emitter, Lifetime(6),
                Gravity((-1.5, 0, 0)),
                Movement(),
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

        color = (0, 0.5, 0.7, 0.6)
        self.gas_emitter = StaticEmitter(
            rate=5,
            template=Particle(
                position=(sx, sy, 0),
                color=color),
            deviation=Particle(
                position=(1, 1, 0),
                velocity=(0.6, 0.2, 0),
                color=(0, 0.03, 0, 0),
                age=1))
        self.gas_emitter_group = ParticleGroup(
            controllers=[self.gas_emitter, Lifetime(6),
                Gravity((1.5, 0, 0)),
                Movement(),
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
        self.particlestest = (
            self.puff_fx,
            self.smoke_fx,
            self.muzzle_fx,
            self.skull_fx,
            self.crit_fx,
            self.blood_fx,
            self.flame_emitter_group,
            self.gas_emitter_group
        )

    def draw_circle(self, x, y, radius):
        iterations = int(2*radius*pi)
        s = sin(2*pi / iterations)
        c = cos(2*pi / iterations)

        dx, dy = radius, 0

        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)
        for i in range(iterations+1):
            glVertex2f(x+dx, y+dy)
            dx, dy = (dx*c - dy*s), (dy*c + dx*s)
        glEnd()

    def render(self, dt):
        """ Rendering method, need to remove game logic """
        if self.loading:
            self.load_screen()
        elif self.mainmenu:
            self.mainmenu.render()
        elif not self.game.paused and not self.mainmenu:
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

            # gluOrtho2D(50, self.width - 50, 50, self.height - 50)
            gluOrtho2D(0, self.width, 0, self.height)

            glColor4f(0, 0, 0, 1)

            glColor4f(0.3, 0.3, 0.3, 1.0)
            glPointSize(3)
            self.setGL("on")
            glColor4f(1, 1, 1, 1)
            self.batches["bg1"].draw()
            self.batches["bg2"].draw()
            self.batches["obs"].draw()
            self.batches["towers"].draw()
            self.batches["mobs"].draw()
            # if self.debug:
            #     self.batches["walls"].draw()
            self.batches["anim"].draw()
            self.batches["fg"].draw()
            self.batches["flying_mobs"].draw()

            # Draw UI #
            # gluOrtho2D(0, self.width, 0, self.height)
            self.userinterface.render()

            self.setGL("off")

            glShadeModel(GL_SMOOTH)
            glEnable(GL_BLEND)
            glDisable(GL_DEPTH_TEST)

            for c in self.particlestest:
                c.draw()
            # self.particle_system.draw()

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

            # Draw mob health bars #
            glColor4f(0.9, 0.2, 0.2, 1.0)
            glLineWidth(3)
            for m in self.game.mobs:
                # glColor4f(0.6, 0.3, 0.3, 0.2 + (m.hp / 100.0) * 0.8)
                if m.hp < m.hp_max and not m.state == "dead" and m.hp > 0.0:
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

            # Draw range circle on active tower
            if self.game.active_tower:
                glColor4f(0.4, 0.5, 0.9, 0.2)
                t = self.game.active_tower
                self.draw_circle(
                    t.x, t.y, t.range
                )
            if self.game.mouse_drag_tower:
                if not self.rectangles:
                    self.game.createGridIndicators()
                glColor4f(0.7, 0.7, 0.9, 0.2)
                self.batches["fg2"].draw()
                glColor4f(0.7, 0.7, 0.3, 0.2)
                self.batches["fg3"].draw()

            else:
                self.batches["fg2"] = pyglet.graphics.Batch()
                self.batches["fg3"] = pyglet.graphics.Batch()
                self.rectangles = None
                self._rectangles = None

            # Update animations #
            for a in self.animations:
                a.update()
                if not a.playing:
                    self.animations.remove(a)

            if self.debug:
                fps_display.draw()

            self.game.updateState()


if __name__ == "__main__":
    window = GameWindow()
    pyglet.clock.schedule_interval(window.render, 1.0 / window.fps)
    pyglet.app.run()

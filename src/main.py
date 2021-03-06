#!/bin/python2
import pyglet   # Version 1.2.2
# from audio import AudioFile  # Sound engine
import os
import glob
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
# try:
#     os.remove('debug.log')
#     os.
# except OSError:
#     pass
import logging
logging.basicConfig(filename='debug.log',
    filemode='w',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)

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
# DEBUG = False
ROOT = os.path.dirname(__file__)
RES_PATH = os.path.join(ROOT, "resources")
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
        self.debug = False
        try:  # to enable multisampling
            gl_config = screen.get_best_config(gl_template)
        except pyglet.window.NoSuchConfigException:
            gl_template = pyglet.gl.Config(alpha_size=8)
            gl_config = screen.get_best_config(gl_template)
            logger.debug('No multisampling.')
        # Create OpenGL context #
        gl_context = gl_config.create_context(None)
        super(GameWindow, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=True,
            vsync=VSYNC
            )
        # GL and graphics variables #
        self.resourcepath = RES_PATH
        self.width = SCREENRES[0]
        self.height = SCREENRES[1]
        self.offset = (0, 0)
        self.fps = FPS
        self.cx, self.cy = 0, 0  # Cursor position
        glClearColor(0.1, 0.1, 0.1, 1)  # Background color
        self.particle_system = default_system
        self.tile_renderer = None
        self.loading = True
        self.drag_rect_start = 0, 0
        self.drag_rect_stop = 0, 0
        self.dragrect = None

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
        self.batches["mm_labels"] = pyglet.graphics.Batch()
        self.batches["anim"] = pyglet.graphics.Batch()
        self.ui_group = pyglet.graphics.OrderedGroup(2)
        self.fg_group = pyglet.graphics.OrderedGroup(1)

        self.loadFonts()    # Loads fonts into memory
        self.loadMapFiles()
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

        logger.info("Creating UI.")
        self.userinterface = UI(self)

        # Spawn main menu
        self.showMainMenu()

        self.loading = False

    def showMainMenu(self):
        logger.debug("Showing main menu.")
        try:
            logger.debug("Clearing old menu screen.")
            self.mainmenu.clearEntries()
        except AttributeError:
            logger.debug("No main menu to clear")
        self.mainmenu = MainMenu(self)
        if self.game.loaded:
            self.mainmenu.addEntry(
                title="Resume", action="resume", top=True
            )
        self.mainmenu.addEntry(title="New Game", action="newgame")
        str_len = len(self.selected_mapfile)
        if str_len > self.mainmenu.max_char:
            string = self.selected_mapfile[str_len - self.mainmenu.max_char:]
        else:
            string = self.selected_mapfile
        self.mainmenu.addEntry(
            title=string, action="selectmap"
        )
        self.mainmenu.addHeader(title="Peace-TW")
        self.mainmenu.addEntry(title="Settings", action="settings")
        self.mainmenu.addEntry(title="Exit", action="quit")
        self.mainmenu.animateIn()

    def showSettingsMenu(self):
        logger.debug("Showing settings menu.")
        try:
            logger.debug("Clearing old menu screen.")
            self.mainmenu.clearEntries()
        except AttributeError:
            logger.debug("No main menu to clear")
        self.mainmenu = MainMenu(self)
        self.mainmenu.addHeader(title="Settings")
        self.mainmenu.addEntry(
            title="Sound: {0}".format(self.sound_enabled),
            action="togglesound"
        )
        self.mainmenu.addEntry(title="Back", action="topmenu")
        self.mainmenu.animateIn()

    def showGameOverMenu(self):
        logger.debug("Showing game-over screen.")
        try:
            logger.debug("Clearing old menu items.")
            self.mainmenu.clearEntries()
        except AttributeError:
            logger.debug("No main menu to clear")
        self.mainmenu = MainMenu(self)
        self.mainmenu.addHeader(title="Game Over")
        self.mainmenu.addEntry(title="Restart", action="newgame")
        self.mainmenu.addEntry(title="Main menu", action="topmenu")
        self.mainmenu.animateIn()

    def flushWindow(self):
        try:
            logger.debug("Removing old particle system.")
            self.particle_system.remove_group(self.flame_emitter_group)
            self.particle_system.remove_group(self.gas_emitter_group)
        except AttributeError as err:
            logger.debug(err)
        except ValueError as err:
            logger.debug(err)
        try:
            pyglet.clock.unschedule(self.particle_system.update)
        except AttributeError as err:
            logger.debug(err)
        except ValueError as err:
            logger.debug(err)
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
        self.batches["mm_labels"] = pyglet.graphics.Batch()
        self.batches["anim"] = pyglet.graphics.Batch()
        self.ui_group = pyglet.graphics.OrderedGroup(2)
        self.fg_group = pyglet.graphics.OrderedGroup(1)

        self.flame_emitter, self.gas_emitter = None, None

    def loadMapFiles(self):
        self.maplist = sorted(glob.glob(os.path.join(RES_PATH, '*.tmx')))
        self.selected_mapfile = self.maplist[0]

    def loadFonts(self):
        logger.info("Loading fonts.")
        pyglet.font.add_file(os.path.join(RES_PATH, 'soft_elegance.ttf'))
        pyglet.font.add_file(os.path.join(RES_PATH, 'visitor1.ttf'))
        self.ui_font = pyglet.font.load('Soft Elegance')
        self.small_font = pyglet.font.load('Visitor TT1 BRK')

    def loadTextures(self):
        logger.info("Loading textures.")
        btn_grey = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'ui', 'btn_grey.png'))
        )
        btn_red = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'ui', 'btn_red.png'))
        )
        btn_green_d = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'ui', 'btn_green_d.png'))
        )
        btn_brown = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'ui', 'btn_brown.png'))
        )
        ws_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'wall_stone.png'))
        )
        sell_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'ui', 'sell.png'))
        )
        gold_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'ui', 'gold.png'))
        )
        upgr_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'ui', 'upgrade.png'))
        )
        p_texture = pyglet.image.load(
            os.path.join(RES_PATH, 'particle.png')
        )
        p_smoke_texture = pyglet.image.load(
            os.path.join(RES_PATH, 'particle_smoke.png')
        )
        p_pang_texture = pyglet.image.load(
            os.path.join(RES_PATH, 'particle_pang.png')
        )
        p_skull_texture = pyglet.image.load(
            os.path.join(RES_PATH, 'particle_skull.png')
        )
        p_lightning_texture = pyglet.image.load(
            os.path.join(RES_PATH, 'particle_lightning.png')
        )
        p_crit_texture = pyglet.image.load(
            os.path.join(RES_PATH, 'crit.png')
        )
        p_blood_texture = pyglet.image.load(
            os.path.join(RES_PATH, 'blood.png')
        )
        tw_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'tower_wood.png'))
        )
        tw_t_img = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'tower_1q_turret.png'))
        )
        tp_img = center_image(pyglet.image.load(
            os.path.join(RES_PATH, 'tower_poison.png'))
        )
        tp_t_img = center_image(pyglet.image.load(
            os.path.join(RES_PATH, 'tower_poison_turret.png'))
        )
        ts_img = center_image(pyglet.image.load(
            os.path.join(RES_PATH, 'tower_splash.png'))
        )
        ts_t_img = center_image(pyglet.image.load(
            os.path.join(RES_PATH, 'tower_splash_turret.png'))
        )
        tc_img = center_image(pyglet.image.load(
            os.path.join(RES_PATH, 'tower_chain.png'))
        )
        mob_1q = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob.png'))
        )
        mob_1w = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1w.png'))
        )
        mob_1e = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1e.png'))
        )
        mob_1r = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1r.png'))
        )
        mob_1a = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1a.png'))
        )
        mob_1s = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1s.png'))
        )
        mob_1d = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1d.png'))
        )
        mob_1f = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1f.png'))
        )
        mob_1z = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1z.png'))
        )
        mob_1x = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1x.png'))
        )
        mob_1c = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1c.png'))
        )
        mob_1v = center_image(
            pyglet.image.load(os.path.join(RES_PATH, 'mob_1v.png'))
        )
        # bg01 = pyglet.image.load(RES_PATH + 'bg01.png')

        self.textures = dict(
            wall_stone=ws_img,
            sell=sell_img,
            gold=gold_img,
            button_grey=btn_grey,
            button_green_jagged=btn_green_d,
            button_red=btn_red,
            button_brown=btn_brown,
            upgrade=upgr_img,
            tower_wood=tw_img,
            tower_wood_turret=tw_t_img,
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
            mob1X=mob_1x,
            mob1C=mob_1c,
            mob1V=mob_1v,
        )

        self.effects = dict(
            puff=p_texture,
            smoke=p_smoke_texture,
            skull=p_skull_texture,
            pang=p_pang_texture,
            crit=p_crit_texture,
            blood=p_blood_texture,
            lightning=p_lightning_texture,
        )


        # Particles and stuff

        self.puff_fx = ParticleCategory(self, "simple", "puff")
        self.smoke_fx = ParticleCategory(self, "simple", "smoke")
        self.muzzle_fx = ParticleCategory(self, "simple", "pang")
        self.lightning_fx = ParticleCategory(self, "simple", "lightning")
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

        # Load images and create image grids for animations #
        # and centers their frame anchor point              #
        death_img = pyglet.image.load(os.path.join(RES_PATH, 'mob_death.png'))
        ping_img = pyglet.image.load(os.path.join(RES_PATH, 'ping_anim.png'))
        pang_img = pyglet.image.load(os.path.join(RES_PATH, 'pang_01_32.png'))
        death_anim = pyglet.image.ImageGrid(death_img, 1, 7)
        ping_anim = pyglet.image.ImageGrid(ping_img, 1, 10)
        pang_anim = pyglet.image.ImageGrid(pang_img, 1, 6)
        for i in death_anim:
            i = center_image(i)
        for i in ping_anim:
            i = center_image(i)
        for i in pang_anim:
            i = center_image(i)

        self.anim = dict(
            mob1Qdeath=death_anim,
            ping=ping_anim,
            pang01=pang_anim
        )

    def loadSFX(self):
        logger.info("Loading sound files.")
        impact1 = pyglet.media.load(
            os.path.join(RES_PATH, "impact1.ogg"), streaming=False
        )
        impact2 = pyglet.media.load(
            os.path.join(RES_PATH, "impact2.ogg"), streaming=False
        )
        dart = pyglet.media.load(
            os.path.join(RES_PATH, "dart.ogg"), streaming=False
        )
        bang1 = pyglet.media.load(
            os.path.join(RES_PATH, "bang1.ogg"), streaming=False
        )
        bang2 = pyglet.media.load(
            os.path.join(RES_PATH, "bang2.ogg"), streaming=False
        )
        pluck = pyglet.media.load(
            os.path.join(RES_PATH, "pluck.ogg"), streaming=False
        )
        bzzt = pyglet.media.load(
            os.path.join(RES_PATH, "bzzt.ogg"), streaming=False
        )
        splat = pyglet.media.load(
            os.path.join(RES_PATH, "splat.ogg"), streaming=False
        )
        click = pyglet.media.load(
            os.path.join(RES_PATH, "click.ogg"), streaming=False
        )
        leak = pyglet.media.load(
            os.path.join(RES_PATH, "leak.ogg"), streaming=False
        )
        # impact1.play()
        # tkSnack.audio.play()
        self.sfx = dict(
            impact1=impact1,
            impact2=impact2,
            dart=dart,
            bang1=bang1,
            bang2=bang2,
            pluck=pluck,
            bzzt=bzzt,
            splat=splat,
            click=click,
            leak=leak
        )

    def playSFX(self, sound="default", volume=1.0):
        if self.sound_enabled:
            logger.debug("Playing sound '{0}'".format(sound))
            for s in self.currently_playing:
                if s.time == 0.0:
                    self.currently_playing.remove(s)
                elif s.id == sound:
                    volume *= 0.7

            i = 0
            while i < len(self.currently_playing):
                volume *= 0.9
                i += 1
            if len(self.currently_playing) < 10:
                playing = self.sfx[sound].play()
                playing.volume = volume
                playing.id = sound
                self.currently_playing.append(playing)

    def getWindowPos(self, x, y):
        """Gets position of a grid coordinate on the window, in pixels"""
        gm, ss = self.game.grid_margin, self.game.squaresize
        ox, oy = self.offset_x, self.offset_y
        x = (ox + x * (ss + gm)) + ss / 2
        y = self.height - ((oy + y * (ss + gm)) + ss / 2)
        return (x, y)

    def getGridPos(self, x, y):
        """Returns grid point at window location"""
        if self.game.grid:
            gw = self.game.grid.dim[0]
            gh = self.game.grid.dim[1]
            mh = self.game.grid.dim[1] - 1
            w = self.game.squaresize
            h = self.game.squaresize
            ox = self.offset_x + 2
            oy = self.offset_y - 2
            for gx in xrange(gw):
                for gy in xrange(gh):
                    # print gx, gy
                    if (
                        x < ox + gx * w + w and
                        x > ox + gx * w
                    ):
                        if (
                            y > self.height - (oy + gy * h + h) and
                            y < self.height - (oy + gy * h)
                        ):
                            return gx, gy
            else:
                raise LookupError("No tower found on {0},{1}".format(x, y))
        else:
            raise ValueError("No grid loaded.")


    def span(self, dx, dy):
        self.offset_x += dx
        self.offset_y -= dy

        self.userinterface.updateOffset()

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

        sx, sy = self.getWindowPos(grid.start[0], grid.start[1])
        for p in self.gas_emitter_group:
            p.position = sx, sy, 0

        gx, gy = self.getWindowPos(grid.goal[0], grid.goal[1])
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

    def drawMobHP(self, mobs):
        glColor4f(0.9, 0.2, 0.2, 1.0)
        glLineWidth(3)
        for m in mobs:
            # glColor4f(0.6, 0.3, 0.3, 0.2 + (m.hp / 100.0) * 0.8)
            if m.hp < m.hp_max and not m.state == "dead" and m.hp > 0.0:
                height = m.image.height // 2
                width = m.image.width // 2
                pyglet.graphics.draw(
                    2,
                    GL_LINES,
                    (
                        'v2f',
                        (
                            m.x - 1 - int((m.hp / m.hp_max) * width),
                            m.y + height,
                            m.x - 1 + int((m.hp / m.hp_max) * width),
                            m.y + height)
                        )
                    )

    def loadingScreen(self):
        logger.debug("Load screen.")
        label = pyglet.text.Label(
                "Loading...", font_name='Visitor TT1 BRK',
                font_size=18,
                x=self.width // 2, y=self.height // 2,
                anchor_x="center", anchor_y="center",
                color=(255, 255, 255, 255)
            )

        glColor4f(0.4, 0.4, 0.3, 0.7)
        self.drawCircle(
            self.width // 2, self.height // 2, 70
        )

        label.draw()

    def pauseGame(self, state):
        self.game.paused = state
        if state:
            self.showMainMenu()
        else:
            if self.mainmenu:
                self.mainmenu.clearEntries()
            self.mainmenu = None

    def quitGame(self):
        logger.info("Exiting...")
        pyglet.app.exit()

    # EVENT HANDLERS #
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            if self.game.loaded:
                self.pauseGame(not self.game.paused)
            else:
                self.quitGame()
            # return True  # Disable ESC to exit
        elif symbol == key.SPACE:
            if self.game.loaded:
                self.pauseGame(not self.game.paused)
        if not self.game.paused:  # Only listen for keys if game is running
            if symbol == key.Q:
                self.game.spawnMob("Q", free=True)
            elif symbol == key.W:
                self.game.spawnMob("W", free=True)
            elif symbol == key.E:
                self.game.spawnMob("E", free=True)
            elif symbol == key.R:
                self.game.spawnMob("R", free=True)
            elif symbol == key.A:
                self.game.spawnMob("A", free=True)
            elif symbol == key.S:
                self.game.spawnMob("S", free=True)
            elif symbol == key.D:
                self.game.spawnMob("D", free=True)
            elif symbol == key.F:
                self.game.spawnMob("F", free=True)
            elif symbol == key.Z:
                self.game.spawnMob("Z", free=True)
            elif symbol == key.X:
                self.game.spawnMob("X", free=True)
            elif symbol == key.C:
                self.game.spawnMob("C", free=True)
            elif symbol == key.V:
                self.game.spawnMob("V", free=True)
            elif symbol == key.F10:
                self.game.gameOver()
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
                        self.game.autospawnRandom,
                        1.0
                    )
                else:
                    pyglet.clock.unschedule(self.game.autospawnRandom)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            if not self.game.paused:
                # First, check if mouse is on a UI element
                if self.userinterface.checkMouse((x, y)):  # returns false if
                    pass                                    # not on a button
                else:
                    Animation(
                        self,
                        self.anim["ping"],
                        x, y
                    )
                    if not self.game.mouse_drag_tower:
                        try:
                            found = False
                            gx, gy = self.getGridPos(x, y)
                            for t in self.game.towers:
                                if [t.gx, t.gy] == [gx, gy]:
                                    found = t
                                    break
                        except LookupError or ValueError as err:
                            logger.debug("Not found.")
                            logger.debug(err)
                            found = False
                        if found:
                            self.game.selected_mouse = found

                        elif self.debug:
                            if not self.game.selected_mouse:
                                tower = SplashTower(
                                    self.game, "Default", x=x, y=y
                                )
                                self.game.placeTower(tower, x, y, new=True)

                    else:
                        self.game.placeTower(
                            self.game.mouse_drag_tower, x, y, new=True
                        )
                        self.game.mouse_drag_tower = None
            elif self.mainmenu:
                pos = (x, y)
                self.mainmenu.checkMouse(pos)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == mouse.LEFT:
            # First, check if mouse is released over a UI element
            t_type = self.userinterface.checkMouse((x, y))
            if self.game.dragging:
                selected = self.game.getDragSelection(self.dragrect)
                self.game.highlightItems(selected)
                self.dragrect = None
                self.drag_rect_start = 0, 0
                self.drag_rect_stop = 0, 0
            else:
                self.game.highlighted = []
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
                    logger.debug("Selling tower")
                    self.game.active_tower.sell()
                    self.game.active_tower = None
                    self.game.selected_mouse = None
                    self.game.mouse_drag_tower = None
                    self.game.dragging = False
                elif t_type == "upgrade":
                    if self.game.active_tower:
                        self.game.active_tower.upgrade()

            elif self.mainmenu:
                under_mouse = self.mainmenu.checkMouse((x, y))
                active = self.mainmenu.active_entry
                if active and active == under_mouse:
                    self.mainmenu.doAction(active)
                elif active:
                    self.mainmenu.onUp(active)
            elif self.game.mouse_drag_tower:
                self.game.active_tower = self.game.mouse_drag_tower
                self.game.placeTower(
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

            if self.mainmenu:
                e = self.mainmenu.checkMouse((x, y))
                if e:
                    if not e == self.mainmenu.active_entry:
                        self.mainmenu.onUp(self.mainmenu.active_entry)
                        self.mainmenu.active_entry = e
                elif self.mainmenu.active_entry:
                    self.mainmenu.onUp(self.mainmenu.active_entry)
                    self.mainmenu.active_entry = False

            elif self.game.selected_mouse and self.debug:
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
                t_type = self.userinterface.checkMouse((x, y))
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
                    try:
                        tower
                        self.userinterface.wipeContextMenu()
                        self.game.active_tower = None
                        self.game.selected_mouse = self.game.mouse_drag_tower
                    except UnboundLocalError:
                        pass
                else:
                    if self.drag_rect_start[0] or self.drag_rect_start[1]:
                        self.drag_rect_stop = x, y
                    else:
                        self.drag_rect_start = x, y

            if not self.game.selected_mouse:
                if not self.userinterface.checkMouse((x, y)):
                    self.userinterface.wipeContextMenu()
                    self.game.active_tower = None

        elif buttons & mouse.RIGHT:
            if self.game.loaded:
                self.span(dx, dy)

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game.mouse_drag_tower:
            self.game.mouse_drag_tower.updatePos(x, y, None, None)
        self.cx, self.cy = x, y
        if self.mainmenu:
            self.mainmenu.getUnderMouse(x, y)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        # glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)
        self.clear()
        self.activate()

        if self.mainmenu:
            self.mainmenu.updateOffset()
        if self.game.loaded:
            self.game.updateGridSettings()

            for t in self.game.towers:
                t.updateOffset()

            for m in self.game.mobs:
                m.updateOffset()

            self.userinterface.updateOffset()

            self.tile_renderer.update_offset()

            grid = self.game.grid
            sx, sy = self.getWindowPos(grid.start[0], grid.start[1])
            for p in self.gas_emitter_group:
                p.position = sx, sy, 0

            gx, gy = self.getWindowPos(grid.goal[0], grid.goal[1])
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
        sx = self.getWindowPos(grid.start[0], grid.start[1])[0]
        sy = self.getWindowPos(grid.start[0], grid.start[1])[1]
        gx = self.getWindowPos(grid.goal[0], grid.goal[1])[0]
        gy = self.getWindowPos(grid.goal[0], grid.goal[1])[1]

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
            self.lightning_fx,
            self.smoke_fx,
            self.muzzle_fx,
            self.skull_fx,
            self.crit_fx,
            self.blood_fx,
            self.flame_emitter_group,
            self.gas_emitter_group
        )

    def drawRangeCircle(self, t):
        glColor4f(0.5, 0.6, 0.8, 0.20)
        self.drawCircle(
            t.x, t.y, t.range
        )

    def drawCircle(self, x, y, radius):
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
            self.loadingScreen()
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
                points, count = self.game.generateGridPathIndicators()
                glColor4f(0.4, 0.4, 0.8, 0.7)
                pyglet.graphics.draw(
                    count,
                    GL_LINES,
                    ('v2f', points)
                )

                points, count = self.game.generateMobPathIndicators()
                glColor4f(0.6, 0.3, 0.3, 0.5)
                pyglet.graphics.draw(
                    count,
                    GL_POINTS,
                    ('v2f', points)
                )

            # Draw mob health bars #
            self.drawMobHP(self.game.mobs)

            # Draw range circle on active tower
            if self.game.active_tower:
                self.drawRangeCircle(self.game.active_tower)
            for t in self.game.highlighted:
                self.drawRangeCircle(t)
            # Draw grid squares when dragging a tower
            if self.game.mouse_drag_tower:
                if not self.rectangles:
                    self.game.createGridIndicators()
                glColor4f(0.7, 0.7, 0.9, 0.2)
                self.batches["fg2"].draw()
                glColor4f(0.7, 0.7, 0.3, 0.2)
                self.batches["fg3"].draw()
            elif self.game.dragging and not self.game.active_tower:
                if (
                    (self.drag_rect_stop[0] or self.drag_rect_stop[0]) and
                    (self.drag_rect_start[0] or self.drag_rect_start[0])
                ):
                    start = self.drag_rect_start
                    stop = self.drag_rect_stop
                    w = start[0] - stop[0]
                    h = start[1] - stop[1]
                    self.dragrect = (
                        create_rectangle(start[0], start[1], w, h, False)
                    )
                    self.batches["fg3"] = pyglet.graphics.Batch()
                    self.batches["fg3"].add(
                        4, GL_QUADS, None,
                        ('v2i', self.dragrect),
                    )
                    glColor4f(0.5, 0.5, 0.3, 0.4)
                    self.batches["fg3"].draw()
            else:   # Clear the squares if tower is no longer dragged
                self.batches["fg2"] = pyglet.graphics.Batch()
                self.batches["fg3"] = pyglet.graphics.Batch()
                self.drag_rect_start = 0, 0
                self.drag_rect_stop = 0, 0
                self.rectangles = None
                self._rectangles = None

            # Update animations #
            for a in self.animations:
                a.update()

            if self.debug:
                fps_display.draw()


if __name__ == "__main__":
    window = GameWindow()
    pyglet.clock.schedule_interval(window.render, 1.0 / window.fps)
    pyglet.app.run()

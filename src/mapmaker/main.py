### Map editor ###

import math
import random
import os,sys,inspect
from collections import OrderedDict
from grid import *
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pyglet
from pyglet.window import key, mouse
from pyglet.gl import *

DEBUG = False
RES_PATH = "../../resources/tiles/"
SCREENRES = (1280, 720)
VSYNC = True
SCREEN_MARGIN = 15  # %

### Get information about the OS and display ###
platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()

### Limit the frames per second to 60 ###
pyglet.clock.set_fps_limit(60)


class Editor(pyglet.window.Window):  # Main game window

    def __init__(self):
        ### Template for multisampling
        gl_template = Config(
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
        super(Editor, self).__init__(
            context=gl_context,
            config=gl_config,
            resizable=True,
            vsync=VSYNC
            )

        glClearColor(0.1, 0.1, 0.1, 1)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)

        self.width, self.height = SCREENRES
        self.squaresize = 32
        self.tiles = []
        self.generateGridSettings()
        self.grid = Grid(self)
        self.loadTextures()

        self.batches = OrderedDict()
        self.batches["0"] = pyglet.graphics.Batch()
        self.batches["1"] = pyglet.graphics.Batch()
        self.batches["2"] = pyglet.graphics.Batch()
        self.batches["3"] = pyglet.graphics.Batch()

        self.bg_group = pyglet.graphics.OrderedGroup(0)

        self.generateTileMenuItems()
        self.generateGridIndicators()
        self.tile_menu_enabled = False

        self.coord_label = pyglet.text.Label()

        self.addBackgroundTile("tsk", (10, 10))

    def loadTextures(self):
        """ Gets list of files in resource directory, and makes a dictionary
            with file names (without extension) as index for loaded images """
        self.texturefiles = []
        for file in os.listdir(RES_PATH):
            if file.endswith(".png"):
                self.texturefiles.append(file)

        self.texturefiles = sorted(self.texturefiles)

        self.textures = dict()
        for fname in self.texturefiles:
            load_file = pyglet.image.load(RES_PATH + fname)
            fname = fname.split(".")[0]
            self.textures[fname] = load_file

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
        rects = []
        for p in self.grid.grid:
            wp_x, wp_y = self.getWindowPos((p[0], p[1]))
            x = wp_x - w // 2
            y = wp_y - w // 2
            r_points = [x, y, x + w, y, x + w, y + w, x, y + w]
            rects = rects + r_points

        self.batches["0"] = pyglet.graphics.Batch()

        rect = self.batches["0"].add(
            len(rects) / 2,
            GL_QUADS,
            self.bg_group,
            ('v2f', (rects))
        )

    def generateTileMenuItems(self):
        tex = self.textures
        items = []
        for key in tex:
            s = pyglet.sprite.Sprite(tex[key], batch=self.batches["3"])
            s.name = key
            s.x, s.y = 0, 0
            items.append(s)

        items.sort(key=lambda x: x.name)
        self.tilemenu_items = items

    def addForegroundTile(self, variant, gridpos):
        tile = ForegroundTile(self, gridpos, "tower_blue")
        x, y = self.getWindowPos(gridpos)
        tile.placeTile(x, y)

        self.tiles.append(tile)

    def addBackgroundTile(self, variant, gridpos):
        tile = BackgroundTile(self, gridpos, "tower_poison")
        x, y = self.getWindowPos(gridpos)
        tile.placeTile(x, y)

        self.tiles.append(tile)

    def getWindowPos(self, (x, y)):
        """Gets position of a grid coordinate on the window, in pixels"""
        gm, ss = self.grid_margin, self.squaresize
        ox, oy = self.offset_x, self.offset_y
        x = (ox + x * (ss + gm)) + ss / 2
        y = self.height - ((oy + y * (ss + gm)) + ss / 2)
        return (x, y)


    """EVENT HANDLERS"""
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            print("Exiting...")
            pyglet.app.exit()

        elif symbol == key.TAB:
            self.tile_menu_enabled = not self.tile_menu_enabled

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        self.coord_label.text = "{0}, {1}".format(x, y)
        self.coord_label.x = x
        self.coord_label.y = y

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

        self.generateGridSettings()
        self.generateGridIndicators()

    def render(self, dt):
        self.clear()
        glColor4f(0.2, 0.2, 0.2, 1)
        self.batches["0"].draw()
        self.batches["2"].draw()

        if self.tile_menu_enabled:
            mx = int(self.width * (SCREEN_MARGIN / 100.0))
            my = int(self.height * (SCREEN_MARGIN / 100.0))
            w, h = self.width, self.height
            glColor4f(0.3, 0.3, 0.3, 0.8)
            pyglet.graphics.draw(
                4,
                GL_QUADS,
                ('v2f', [mx, my, w - mx, my, w - mx, h - my, mx, h - my])
            )

            mx += 10
            my += 10
            max_x = w - mx
            max_y = h - my
            ss = self.squaresize + 3
            i = 0
            for s in self.tilemenu_items:
                s.x = (mx + ss * i)
                s.y = max_y - ss
                i += 1
                s.draw()

        self.coord_label.draw()

            # self.batches["3"].draw()



class ForegroundTile(pyglet.sprite.Sprite):

    def __init__(self, window, gridpos, variant):
        super(ForegroundTile, self).__init__(
            window.textures[variant], batch=window.batches["2"]
        )
        self.gpos = gridpos

    def placeTile(self, x, y):
        self.x, self.y = x, y


class BackgroundTile(pyglet.sprite.Sprite):

    def __init__(self, window, gridpos, variant):
        super(BackgroundTile, self).__init__(
            window.textures[variant], batch=window.batches["2"]
        )
        self.gpos = gridpos

    def placeTile(self, x, y):
        self.x, self.y = x, y

if __name__ == "__main__":
    window = Editor()
    pyglet.clock.schedule_interval(window.render, 1.0/60.0)
    pyglet.app.run()
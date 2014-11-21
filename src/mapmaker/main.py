### Map editor ###

import math
import random
import os,sys,inspect
from collections import OrderedDict
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pyglet
from pyglet.window import key, mouse
from pyglet.gl import *

DEBUG = False
RES_PATH = "../../resources/"
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

        self.width, self.height = SCREENRES
        self.tiles = []
        self.generateGridSettings()
        self.loadTextures()

        self.batches = OrderedDict()
        self.batches["0"] = pyglet.graphics.Batch()
        self.batches["1"] = pyglet.graphics.Batch()
        self.batches["2"] = pyglet.graphics.Batch()

        self.test = pyglet.sprite.Sprite(
            self.textures["pang_01"],
            50, 50,
            batch=self.batches["2"]
        )

        self.addBackgroundTile("tsk", (10, 10))

    def loadTextures(self):
        """ Gets list of files in resource directory, and makes a dictionary
            with file names (without extension) as index for loaded images """
        self.texturefiles = []
        for file in os.listdir(RES_PATH):
            if file.endswith(".png"):
                self.texturefiles.append(file)

        self.textures = dict()
        for fname in self.texturefiles:
            load_file = pyglet.image.load(RES_PATH + fname)
            fname = fname.split(".")[0]
            self.textures[fname] = load_file

        print self.textures


    def generateGridSettings(self):
        """ These control the grid that is the game window """
        w, h, gm, ssize = self.width, self.height, 1, 32
        self.squaresize = ssize
        self.grid_margin = gm
        self.grid_dim = (32, 20)
        self.offset_x = (w - self.grid_dim[0] * (ssize + gm)) // 2
        self.offset_y = (h - self.grid_dim[1] * (ssize + gm)) // 2

    def addForegroundTile(self, variant, gridpos):
        tile = ForegroundTile(self, gridpos, "pang_01")
        x, y = self.getWindowPos(gridpos)
        tile.placeTile(x, y)

        self.tiles.append(tile)

    def addBackgroundTile(self, variant, gridpos):
        tile = BackgroundTile(self, gridpos, "particle_pang")
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

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def render(self, dt):
        self.batches["2"].draw()


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
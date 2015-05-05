"""
This is tested on pyglet 1.2 and python 2.7.
Leif Theden "bitcraft", 2012-2014

Rendering demo for the TMXLoader.

This should be considered --alpha-- quality.  I'm including it as a
proof-of-concept for now and will improve on it in the future.

Notice: slow!  no transparency!
"""
import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

from pytmx import *
from pytmx.util_pyglet import load_pyglet
import pyglet

class TiledRenderer(object):
    """
    Super simple way to render a tiled map with pyglet

    no shape drawing yet
    """
    def __init__(self, filename):
        tm = load_pyglet(filename)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm
        self.batches = []
        self.sprites = []
        self.generate_sprites()

    def create_rectangle(cx, cy, w, h):
        rectangle = [
                    cx - w // 2, cy - h // 2,
                    cx - w // 2, cy + h // 2,
                    cx + w // 2, cy + h // 2,
                    cx + w // 2, cy - h // 2,
                ]
        return rectangle

    def draw_lines(self, color, closed, points, width):
        pass

    def generate_sprites(self):
        self.batches = []
        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        mh = self.tmx_data.height - 1
        mw = self.tmx_data.width
        draw_rect = self.draw_rect
        draw_lines = self.draw_lines

        rect_color = (255, 0, 0)
        poly_color = (0, 255, 0)

        for layer in self.tmx_data.visible_layers:
            batch = pyglet.graphics.Batch()
            self.batches.append(batch)
            # draw map tile layers
            if isinstance(layer, TiledTileLayer):

                # iterate over the tiles in the layer
                for x, y, image in layer.tiles():
                    print("Adding sprite")
                    y = mh - y
                    x = x * tw
                    y = y * th
                    sprite = pyglet.sprite.Sprite(
                        image, batch=batch, x=x, y=y
                    )
                    self.sprites.append(sprite)

            # draw object layers
            elif isinstance(layer, TiledObjectGroup):

                # iterate over all the objects in the layer
                for obj in layer:
                    logger.info(obj)

                    # objects with points are polygons or lines
                    if hasattr(obj, 'points'):
                        print("Drawing points")
                        draw_lines(poly_color, obj.closed, obj.points, 3)

                    # some object have an image
                    elif obj.image:
                        print("Drawing image")
                        y = mh - obj.y
                        x = obj.x * tw
                        y = y * th
                        sprite = pyglet.sprite.Sprite(
                            obj.image, batch=batch,
                            x=x, y=y)
                        self.sprites.append(sprite)

                    # draw a rect for everything else
                    else:
                        print("Drawing rectangle")
                        y = mh - obj.y
                        x = obj.x * tw
                        y = y * th
                        r = self.create_rectangle(
                            x, y, obj.width, obj.height
                        )
                        batch.add(
                            4, pyglet.graphics.gl.GL_QUADS, None,
                            ('v2i', r),
                        )

            # draw image layers
            elif isinstance(layer, TiledImageLayer):
                if layer.image:
                    x = mw // 2
                    y = mh // 2
                    sprite = pyglet.sprite.Sprite(
                        layer.image, batch=batch, x=x, y=y
                    )
                    self.sprites.append(sprite)

    def draw(self):
        if self.batches:
            for b in self.batches:
                b.draw()


class SimpleTest(object):
    def __init__(self, filename):
        self.renderer = None
        self.running = False
        self.dirty = False
        self.exit_status = 0
        self.load_map(filename)

    def load_map(self, filename):
        self.renderer = TiledRenderer(filename)

        logger.info("Objects in map:")
        for obj in self.renderer.tmx_data.objects:
            logger.info(obj)
            for k, v in obj.properties.items():
                logger.info("%s\t%s", k, v)

        logger.info("GID (tile) properties:")
        for k, v in self.renderer.tmx_data.tile_properties.items():
            logger.info("%s\t%s", k, v)

    def draw(self):
        self.renderer.draw()


def all_filenames():
    import os.path
    import glob
    _list = glob.glob(os.path.join('data', '0.9.1', '*.tmx'))
    try:
        while _list:
            yield _list.pop(0)
    except IndexError:
        pyglet.app.exit()


class TestWindow(pyglet.window.Window):
    def on_draw(self):
        if not hasattr(self, 'filenames'):
            self.filenames = all_filenames()
            self.next_map()

        self.clear()
        self.contents.draw()

    def next_map(self):
        try:
            self.contents = SimpleTest(next(self.filenames))
        except StopIteration:
            pyglet.app.exit()

    def on_key_press(self, symbol, mod):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
        else:
            self.next_map()


if __name__ == '__main__':
    window = TestWindow(600, 600)
    pyglet.app.run()

from pytmx import *
from pytmx.util_pyglet import load_pyglet
from pyglet.sprite import Sprite
from pyglet.image import ImageDataRegion
from functions import *
from main import logger


class TiledRenderer(object):

    """Super simple way to render a tiled map with pyglet
    no shape drawing yet"""

    def __init__(self, window, filename):
        tm = load_pyglet(filename)
        self.size = tm.width * tm.tilewidth, tm.height * tm.tileheight
        self.tmx_data = tm
        self.window = window
        self.sprites = []
        self.loadmap()

    def draw_rect(self, color, rect, width):
        pass

    def draw_lines(self, color, closed, points, width):
        pass

    def update_offset(self):
        for s in self.sprites:
            if s.imagelayer:
                s.x = self.window.offset_x
                s.y = self.window.offset_y
            else:
                s.x, s.y = self.window.get_windowpos(s.gx, s.gy)

    def loadmap(self):

        tw = self.tmx_data.tilewidth
        th = self.tmx_data.tileheight
        mh = self.tmx_data.height - 1
        draw_rect = self.draw_rect
        draw_lines = self.draw_lines
        offset_x, offset_y = 0, 0

        rect_color = (255, 0, 0)
        poly_color = (0, 255, 0)

        for l in self.tmx_data.layers:
            if isinstance(l, TiledTileLayer) and l.name == "Obstacles":
                logger.debug("Removing obstacles from game grid.")
                for x, y, image in l.tiles():
                    self.window.game.tiles_no_walk.append((x, y))
                    self.window.game.tiles_no_build.append((x, y))
            elif isinstance(l, TiledTileLayer) and l.name == "Flightpath":
                logger.debug("Fligh path included in map, importing.")
                self.window.game.flightgrid = []
                for x, y, image in l.tiles():
                    self.window.game.flightgrid.append((x, y))

        for layer in self.tmx_data.visible_layers:
            nw, nb = False, False   # nowalk, nobuild
            spawn, goal = False, False
            if layer.name == "Background":
                batch = self.window.batches["bg1"]
            elif layer.name == "Background2":
                batch = self.window.batches["bg2"]
            elif layer.name == "Obstacles":
                batch = self.window.batches["obs"]
                # nw, nb = True, True
            elif layer.name == "Spawn":
                batch = self.window.batches["obs"]
                nb = True
                spawn = True
            elif layer.name == "Goal":
                batch = self.window.batches["obs"]
                nb = True
                goal = True
            elif layer.name == "Foreground":
                batch = self.window.batches["fg"]
            else:
                logger.error("Layer not recognized, skipping {0}".format(
                        layer.name
                    )
                )
                break
            # draw map tile layers
            if isinstance(layer, TiledTileLayer):
                if not layer.name == "Obstacles":
                    # iterate over the tiles in the layer
                    for x, y, image in layer.tiles():
                        if nw:
                            self.window.game.tiles_no_walk.append((x, y))
                        if nb:
                            self.window.game.tiles_no_build.append((x, y))
                        gx, gy = x, y
                        y = mh - y
                        x = x * tw
                        y = y * th
                        x += offset_x
                        y += offset_y
                        # image.blit(x * tw, y * th)
                        image = center_image(image)
                        sprite = Sprite(image, batch=batch, x=x, y=y)
                        sprite.imagelayer = False
                        sprite.gx, sprite.gy = gx, gy
                        self.sprites.append(sprite)
                        if spawn:
                            self.window.game.spawn = (gx, gy)
                        elif goal:
                            self.window.game.goal = (gx, gy)

            # draw object layers
            elif isinstance(layer, TiledObjectGroup):

                # iterate over all the objects in the layer
                for obj in layer:
                    logger.info(obj)

                    # objects with points are polygons or lines
                    if hasattr(obj, 'points'):
                        draw_lines(poly_color, obj.closed, obj.points, 3)

                    # some object have an image
                    elif obj.image:
                        # obj.image.blit(obj.x, pixel_height - obj.y)
                        sprite = Sprite(image, batch=batch, x=x * tw, y=y * th)

                    # draw a rect for everything else
                    else:
                        draw_rect(rect_color,
                                  (obj.x, obj.y, obj.width, obj.height), 3)

            # draw image layers
            elif isinstance(layer, TiledImageLayer):
                if layer.image:
                    # if isinstance(layer.image, ImageDataRegion):
                    #     print "heidu"
                    #     image = layer.image.get_texture()
                    # else:
                    image = layer.image
                    # image = center_image(image)
                    x = self.window.width // 2
                    y = self.window.height // 2
                    sprite = Sprite(image, batch=batch, x=x, y=y)
                    sprite.imagelayer = True
                    sprite.gx, sprite.gy = None, None
                    self.sprites.append(sprite)

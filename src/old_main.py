#!/usr/bin/python2

import pyglet
import math
import random
import pypf
import resources
from collections import OrderedDict
from pyglet.window import key, mouse
from pyglet.gl import *
from functions import *

DEBUG = False
#DEBUG = True  # To see what's going on, and events called
FULLSCREEN = True
SHOWGRID = False
VSYNC = True
SCREENRES = (1280, 720)
SCREEN_MARGIN = 15  # percentage
SCREEN_MARGIN_X = (SCREENRES[0] * SCREEN_MARGIN) // 100
SCREEN_MARGIN_Y = (SCREENRES[1] * SCREEN_MARGIN) // 100
SQUARE_SIZE = 32
GRID_MARGIN = 1
GRID_DIM = [(SCREENRES[0]-SCREEN_MARGIN_X)//(SQUARE_SIZE + GRID_MARGIN),
                (SCREENRES[1]-SCREEN_MARGIN_Y)//(SQUARE_SIZE + GRID_MARGIN)
            ]
GRID_DIM = [32, 20]
offset_x = (SCREENRES[0] - GRID_DIM[0] * (SQUARE_SIZE + GRID_MARGIN)) // 2
offset_y = (SCREENRES[1] - GRID_DIM[1] * (SQUARE_SIZE + GRID_MARGIN)) // 2
pyglet.clock.set_fps_limit(60)

platform = pyglet.window.get_platform()
display = platform.get_default_display()
screen = display.get_default_screen()
fps_display = pyglet.clock.ClockDisplay()

template = pyglet.gl.Config(sample_buffers=1, samples=4, alpha_size=8)
try:
    config = screen.get_best_config(template)
except pyglet.window.NoSuchConfigException:
    template = pyglet.gl.Config(alpha_size=8)
    config = screen.get_best_config(template)
    print "No multisampling."

context = config.create_context(None)
window = pyglet.window.Window(SCREENRES[0], SCREENRES[1], context=context,
        config=config, resizable=True, vsync=VSYNC
    )

pyglet.gl.glClearColor(0.1, 0.1, 0.1, 1)  # BG-color


batches = OrderedDict()
batches["fg"] = pyglet.graphics.Batch()
batches["bg"] = pyglet.graphics.Batch()
bg = pyglet.graphics.OrderedGroup(0)
fg = pyglet.graphics.OrderedGroup(1)

def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width//2
    image.anchor_y = image.width//2

image = pyglet.resource.image('no_texture.png')
tower_blue = pyglet.resource.image('tower_blue.png')
wall_stone = pyglet.resource.image('wall_stone.png')
tower_wood = pyglet.resource.image('tower_wood.png')
mob_img = pyglet.resource.image('mob.png')
death_img = pyglet.resource.image('mob_death.png')
death_anim = pyglet.image.ImageGrid(death_img, 1, 7)
for i in death_anim:
    center_image(i)
center_image(image)
center_image(tower_blue)
center_image(wall_stone)
center_image(tower_wood)
center_image(mob_img)


def get_gridpos(x, y):
    x = (offset_x + x * (SQUARE_SIZE + GRID_MARGIN)) + SQUARE_SIZE//2
    y = SCREENRES[1] - ((offset_y + y * (SQUARE_SIZE + GRID_MARGIN)) + SQUARE_SIZE//2)

    return [x, y]

def place_tower(t, x, y):
    placed = False
    dist = 1000
    for g in grid.grid:
        if not g == grid.goal or g == grid.start:
            gx = get_gridpos(g[0], g[1])[0]
            gy = get_gridpos(g[0], g[1])[1]
            if get_dist(gx, gy, x, y) < dist:
                dist = get_dist(gx, gy, x, y)
                placed = False
                if dist <= SQUARE_SIZE:
                    placed = True
                    new_g = g
                    new_rg = [gx, gy]


    if placed:
        t.selected = False
        t.updatePos(new_rg[0], new_rg[1], new_g[0], new_g[1])
        towers.append(t)

        update = []
        for m in mobs:  # Forces mobs to refresh path if tower is in the way
            if len(m.path) > 0:
                for p in m.path:
                    if m.path.index(p) > m.path.index(m.currentpoint):
                        if new_rg == p:
                            update.append(m)
            else:
                for p in grid.path:
                    if grid.path.index(p) > grid.path.index(m.currentpoint):
                        if new_rg == p:
                            update.append(m)

        grid.update(towers, walls)
        for m in update:
            m.updateTarget(grid)
        print("Tower placed at [{0},{1}]".format(new_rg[0], new_rg[1]))


# Grid indicators
w, m = SQUARE_SIZE, GRID_MARGIN
for yi in range(0, GRID_DIM[1]):
    for xi in range(0, GRID_DIM[0]):
        x = offset_x + xi * (w + m)
        y = offset_y + yi * (w + m)
        dot = batches["fg"].add(1, GL_POINTS, fg,
            ('v2i', (get_gridpos(xi, yi)))
            )
        if SHOWGRID:
            text = pyglet.text.Label("{0},{1}".format(xi,yi),
                                        font_name="Lato Regular",
                                        font_size=8,
                                        x=get_gridpos(xi,yi)[0],
                                        y=get_gridpos(xi,yi)[1],
                                        anchor_x = "center",
                                        anchor_y = "center",
                                        batch=batches["fg"], group=fg)
        rect = batches["bg"].add(4, GL_QUADS, bg,
            ('v2i', (x, y,
                     x + w, y,
                     x + w, y + w,
                     x, y + w))
        )


# class Game(pyglet.window.Window):
#     'The main game instance'
#     def __init__(self, width=SCREENRES[0], height=SCREENRES[0], context=context, config=config,
#                     resizable=True, vsync= VSYNC):
#         print "Made game!"

# yeah = Game()


class Tower:
    'The main tower constructor'
    def __init__(self, name, x=None, y=None):
        self.name = name
        self.size = 32
        self.dmg = 5.0
        self.crit = 15
        self.spd = 0.6
        self.cd = False
        self.dmg_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.range = 100
        self.target = None
        self.turret_size = 14
        self.turret_color = (0.28, 0.22, 0.16, 1)
        self.gx = x
        self.gy = y
        if x and y:
            self.x = x
            self.y = y
        else:
            self.x = window.width//2
            self.y = window.height//2
        self.sprite = pyglet.sprite.Sprite(tower_wood, batch=batches["fg"], group=fg)
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.selected = False
        self.angle = 0
        self.sprite.rotation = self.angle

    def updatePos(self, x, y, gx, gy):
        self.x = x
        self.y = y
        self.gx = gx
        self.gy = gy
        self.sprite.x = self.x
        self.sprite.y = self.y

    def setCD(self, n):
        self.cd = True
        self.cd_count = n * 60  # FPS

    def resetCD(self):
        if self.cd:
            if self.cd_count > 0:
                self.cd_count -= 1
            else:
                self.cd_count = 0
                self.cd = False


class Wall:
    def __init__(self, x, y):
        self.x = get_gridpos(x, y)[0]
        self.y = get_gridpos(x, y)[1]
        self.gx = x
        self.gy = y
        self.sprite = pyglet.sprite.Sprite(wall_stone, batch=batches["fg"], group=fg)
        self.sprite.x = self.x
        self.sprite.y = self.y



class Mob:
    'The main mob constructor'
    def __init__(self, variant, debug=True):
        if len(grid.path) > 0:
            self.x = get_gridpos(grid.start[0], grid.start[1])[0]
            self.y = get_gridpos(grid.start[0], grid.start[1])[1]
            self.currentpoint = grid.start
            self.target_pos = grid.path[0]
        else:
            self.x = get_gridpos(grid.start[0], grid.start[1])[0]
            self.y = get_gridpos(grid.start[0], grid.start[1])[1]
            self.currentpoint = grid.start
            self.target_pos = self.currentpoint
        self.lastpoint = None
        self.rx = float(self.x)
        self.ry = float(self.y)
        self.sprite = pyglet.sprite.Sprite(mob_img, batch=batches["fg"], group=fg)
        self.state = "alive"
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.variant = variant
        self.hp = 100.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.0
        self.point = 0
        self.path = []
        self.returnpath = []
        self.debug = debug
        if self.debug:
            print "Spawning mob!"

    def updatePos(self, grid):
        if len(self.path) > 0:
            points = self.path
            self.spd = 2.0
        else:
            points = grid.path
            self.spd = 1.0

        if self.target_pos in points and self.target_pos in grid.grid:
            target_point = get_gridpos(self.target_pos[0], self.target_pos[1])

            if self.x > window.width or self.y > window.height \
                or self.x < 0 or self.y < 0:
                self.state = "dead"
            
            if get_dist(target_point[0], target_point[1], self.x, self.y) < 2:
                if self.point < len(points) - 1:
                    self.lastpoint = self.currentpoint
                    self.currentpoint = self.target_pos
                    self.target_pos = points[self.point]
                    self.point = points.index(self.currentpoint) + 1
                else:
                    if len(self.path) == 0:
                        print "Reached goal!!!"
                        self.state = "dead"
                    else:
                        if self.debug:
                            print "End of path, attempting to rejoin route."
                        self.path = []
                        self.updateTarget(grid)


            else:
                rads = get_angle(self.rx, self.ry,\
                                    target_point[0], target_point[1]
                                )
                self.rx = self.rx + self.spd * math.cos(rads)
                self.ry = self.ry - self.spd * math.sin(rads)

            self.x = int(self.rx)
            self.y = int(self.ry)
            self.sprite.x = self.x
            self.sprite.y = self.y

        else:
            if self.debug:
                print "Mob location not in route, getting new route."
            self.updateTarget(grid)

    def updateTarget(self, grid):
        if self.debug:
            print "Updating target for mob."
            print "currentpoint: {0}".format(self.currentpoint)
            print "target_pos: {0}".format(self.target_pos)
            print "point: {0}".format(self.point)
        points = grid.path
        short_dist = window.width
        find_way = True
        for p in points:
            pos = get_gridpos(p[0], p[1])
            dist = get_dist(pos[0], pos[1], self.x, self.y)
            #if get_griddist(p, self.)
            if dist < short_dist:
                short_dist = dist
                self.target_pos = p
                if dist <= SQUARE_SIZE+2:
                    if self.debug:
                        "Nearby point found, no need to calculate route."
                    self.path = []
                    self.point = points.index(p)
                    self.currentpoint = p
                    find_way = False

        if find_way:  # If further than a block away from goal, recalculate path
            self.point = 0
            self.path = pypf.get_path(grid.grid, self.currentpoint, self.target_pos)


class Animate:
    'The main animation constructor'

    def __init__(self, anim, x, y):
        self.x = x
        self.y = y
        self.playing = True
        self.timer = 0
        self.anim = anim
        self.sprite = pyglet.sprite.Sprite(self.anim[self.timer], batch=batches["fg"], group=fg)
        self.sprite.x = self.x
        self.sprite.y = self.y

    def update(self):
        if self.timer < len(self.anim) - 1:
            self.timer += 1
            self.sprite = pyglet.sprite.Sprite(self.anim[self.timer], batch=batches["fg"], group=fg)
            self.sprite.x = self.x
            self.sprite.y = self.y
        else:
            self.playing = False

class Grid:
    'The main grid constructor'
    def __init__(self, dimensions):
        self.grid = []
        self.path = []
        self.dim = dimensions
        self.generate()
        self.start = [self.dim[0]//2, 0]
        self.goal = [self.dim[0]//2, self.dim[1]-1]


    def generate(self):
        self.grid = []
        for xi in range (0, self.dim[0]):
            for yi in range(0, self.dim[1]):
                self.grid.append([xi,yi])

    def update(self, towers, walls):
        print "generating new grid"
        self.generate()
        tc, wc = 0, 0
        for t in towers:
            for g in self.grid:  # Checks for towers in grid, removes them
                if t.gx == g[0] and t.gy == g[1]:
                    self.grid.remove(g)
                    tc += 1
        print "removed {0} grid points for towers".format(tc)
        for w in walls:
            for g in self.grid:  # Checks for towers in grid, removes them
                if w.gx == g[0] and w.gy == g[1]:
                    self.grid.remove(g)
                    wc += 1
        print "removed {0} grid points for walls".format(wc)
        self.path = pypf.get_path(self.grid, self.start, self.goal)

mobs = []  # List of mobs
towers = []  # List of towers
walls = []  # List of walls
walls_grid = [[4,1], [4,2], [4,3], [4,4], [4,5], [4,6], [5,6], [6,6], [7,6], [8,6], [9,6], [10,6], [11,6], [11,7], [11,8], [11,9], [12,9], [13,9], [14,9], [15,9], [16,9], [17,9], [18,9], [18,10], [18,11], [18,12], [19,12], [20,12]]
for g in walls_grid:
    wall = Wall(g[0], g[1])
    walls.append(wall)
grid = Grid(GRID_DIM)  # Makes a list of tuples containing square id
grid.update(towers, walls)  # Update list to remove towers
animations = []  # List of animation sprites
p1 = get_gridpos(GRID_DIM[0]//2, GRID_DIM[1])
p2 = get_gridpos(GRID_DIM[0]//2, GRID_DIM[1]//2)
p3 = get_gridpos(GRID_DIM[0]//4, GRID_DIM[1]//2)
p4 = get_gridpos(GRID_DIM[0]//4, GRID_DIM[1]//4)
p5 = get_gridpos(GRID_DIM[0]//2, GRID_DIM[1]//4)
p6 = get_gridpos(GRID_DIM[0]//2, 0)
# path_points = [p1, p2, p3, p4, p5, p6]
path_points = [p1, p6]

label = pyglet.text.Label('PEACE-TW',
                            font_name='Lato Regular',
                            font_size=36,
                            x=window.width//2, y=50,
                            anchor_x='center', anchor_y='center')

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.ESCAPE:
        print "Exiting..."
        # return True  # Disable ESC to exit
    elif symbol == key.ENTER:
        tower = Tower("Default")
        towers.append(tower)
    elif symbol == key.SPACE:
        mob = Mob("YAY")
        mobs.append(mob)
    elif symbol == key.F11:
        window.set_fullscreen(not window.fullscreen)
    elif symbol == key.LEFT:
        t = Tower("Default", x=random.randint(0, GRID_DIM[0]), y=random.randint(0, GRID_DIM[1]))
        towers.append(t)


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        selected = False
        for tower in towers:
            if x < tower.x + tower.size//2 and x > tower.x - tower.size//2:
                if y < tower.y + tower.size//2 and y > tower.y - tower.size//2:
                    tower.selected = True
            if tower.selected:
                selected = True
                break

        if not selected:
            tower = Tower("Default", x=x, y=y)
            place_tower(tower, x, y)
        # else:
        #     self.sprite.delete()
        #     towers.remove(self)
        #     grid.update(towers)
        #     print "Tower removed"
    elif button == mouse.RIGHT:
        tower = Tower("Default", x=x, y=y)
        towers.append(tower)


@window.event
def on_mouse_release(x, y, button, modifiers):
    if button == mouse.LEFT:
        for t in towers:
            if t.selected:
                placed = False
                dist = 1000
                for g in grid.grid:
                    if not g == grid.goal or g == grid.start:
                        gx = get_gridpos(g[0], g[1])[0]
                        gy = get_gridpos(g[0], g[1])[1]
                        if get_dist(gx, gy, x, y) < dist:
                            dist = get_dist(gx, gy, x, y)
                            placed = False
                            if dist <= SQUARE_SIZE:
                                placed = True
                                new_g = g
                                new_rg = [gx, gy]


                t.selected = False

                if placed:
                    t.updatePos(new_rg[0], new_rg[1], new_g[0], new_g[1])
                    grid.update(towers, walls)
                    for m in mobs:
                        for p in grid.path:
                            if grid.path.index(p) >= m.point or p in m.path:
                                if new_g == p:
                                    m.updateTarget(grid)

                    print("Tower placed at [{0},{1}]".format(new_g[0], new_g[1]))
                else:
                    t.sprite.delete()
                    towers.remove(t)
                    grid.update(towers, walls)
                    print "Tower removed"


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & mouse.LEFT:
        for t in towers:
            if t.selected:
                t.updatePos(x, y, None, None)

@window.event
def on_resize(width, height):
    pass

@window.event
def on_draw():
    pass


def render(dt):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    pyglet.gl.glColor4f(0.12, 0.12, 0.12, 1)
    batches["bg"].draw()
    pyglet.gl.glColor4f(0.3, 0.3, 0.3, 1)
    batches["fg"].draw()

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    glLineWidth(3)

    label.draw()

    pyglet.gl.glColor4f(0.3, 0.3, 0.3, 0.7)  # Line color
    for t in towers:
        pyglet.gl.glColor4f(t.turret_color[0],t.turret_color[1],t.turret_color[2],t.turret_color[3])
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
            ('v2i', (t.x, t.y, int(t.x + t.turret_size * math.cos(math.radians(t.angle))), int(t.y + t.turret_size * math.sin(math.radians(t.angle)))))
        )

    for m in mobs:
        m.updatePos(grid)  # Update movement
        pyglet.gl.glColor4f(0.6, 0.3, 0.3, 0.2 + (m.hp / 100.0) * 0.8)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
            ('v2i', (m.x - 1 - int((m.hp / 100.0) * 8),
                m.y + 10,
                m.x - 1 + int((m.hp / 100.0) * 8),
                m.y + 10)))
        if m.state == "dead":
            anim = Animate(death_anim, m.x, m.y)
            animations.append(anim)
            print "DEAD"
            mobs.remove(m)



    for t in towers:
        if not t.target:  # if tower has no target
            for m in mobs:
                dist = get_dist(m.x, m.y, t.x, t.y)
                if dist <= t.range:
                    t.target = m
                    break
        else:  # if tower has a target, do something
            dist = get_dist(t.target.x, t.target.y, t.x, t.y)
            if dist > t.range:
                t.target = None

            if t.target not in mobs:
                t.target = None

            if t.target:
                t.target = doDamage(t, t.target)  # Do damage
                rads = get_angle(t.x, t.y, t.target.x, t.target.y)
                t.angle = -math.degrees(rads)
                if t.target.state == "dead":
                    t.target = None
        t.resetCD()

    for a in animations:
        a.update()
        if not a.playing:
            animations.remove(a)

    fps_display.draw()


if DEBUG:
    window.push_handlers(pyglet.window.event.WindowEventLogger())

pyglet.clock.schedule_interval(render, 1.0/60.0)
pyglet.app.run()
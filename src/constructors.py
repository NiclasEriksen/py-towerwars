import math

class Tower:
    'The main tower constructor'
    towerCount = 0

    def __init__(self, window, name):
        self.name = name
        self.size = 32
        self.dmg = 1.0
        self.spd = 1.0
        self.dmg_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.range = 100
        self.target = None
        self.x = window.width//2
        self.y = window.height//2
        self.sprite = pyglet.sprite.Sprite(tower_blue, batch=batch, group=fg)
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.selected = False
        self.angle = 0
        self.sprite.rotation = self.angle


    def updatePos(self, x, y):
        self.x = x
        self.y = y
        self.sprite.x = self.x
        self.sprite.y = self.y

class Mob:
    'The main mob constructor'
    mobCount = 0

    def __init__(self, window, variant):
        self.x = 16
        self.y = window.height//2
        self.rx = float(self.x)
        self.ry = float(self.y)
        self.sprite = pyglet.sprite.Sprite(mob_img, batch=batch, group=fg)
        self.state = "alive"
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.variant = variant
        self.hp = 100.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.0
        self.point = 0
        print "Spawning mob!"

    def updatePos(self, points):
        #self.x += 1
        #self.sprite.x += 1
        if self.x > window.width or self.y > window.height \
            or self.x < 0 or self.y < 0:
            self.state = "dead"
        if get_dist(points[self.point][0], points[self.point][1], self.x, self.y) < 2:
            if self.point < len(points) - 1:
                self.point += 1
            else:
                self.state = "dead"
        else:
            dx = points[self.point][0] - self.rx
            dy = points[self.point][1] - self.ry
            rads = math.atan2(-dy,dx)
            rads %= 2*math.pi
            print self.x
            self.rx = self.rx + self.spd * math.cos(rads)
            print self.y
            self.ry = self.ry - self.spd * math.sin(rads)

        self.x = int(self.rx)
        self.y = int(self.ry)
        self.sprite.x = self.x
        self.sprite.y = self.y


class Animate:
    'The main animation constructor'

    def __init__(self, anim, x, y):
        self.x = x
        self.y = y
        self.playing = True
        self.timer = 0
        self.anim = anim
        self.sprite = pyglet.sprite.Sprite(self.anim[self.timer], batch=batch, group=fg)
        self.sprite.x = self.x
        self.sprite.y = self.y

    def update(self):
        if self.timer < len(self.anim) - 1:
            self.timer += 1
            self.sprite = pyglet.sprite.Sprite(self.anim[self.timer], batch=batch, group=fg)
            self.sprite.x = self.x
            self.sprite.y = self.y
        else:
            self.playing = False
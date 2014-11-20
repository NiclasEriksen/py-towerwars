from pyglet.sprite import Sprite
import random  # For crits and such
from functions import *
from lepton import Particle
import animation

n_particle = Particle(
    velocity=(0,20.0,0), 
    color=(0.55 ,0.50, 0.45, 0.5)
)


class Tower(Sprite):

    'The main tower constructor'

    def __init__(self, game, name="Default", x=None, y=None):
        super(Tower, self).__init__(
            game.textures["tower_wood"],
            batch=game.batches["fg"],
            group=game.fg_group
        )
        self.name = name
        self.game = game
        self.size = game.squaresize
        self.dmg = 4.0
        self.crit = 15
        self.spd = 0.4
        self.cd = False
        self.dmg_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.range = int(game.squaresize * 3)
        self.target = None
        self.turret_size = 14
        self.turret_width = 3
        self.turret_color = (0.28, 0.22, 0.16, 1)
        self.gx = x
        self.gy = y
        if x and y:  # If position is supplied, set it
            self.x = x
            self.y = y
        else:  # Sets the tower position to cursor position
            self.x = self.game.cx
            self.y = self.game.cy
        self.selected = False
        self.angle = random.randrange(0, 360)

    def updatePos(self, x, y, gx, gy):
        self.x = x
        self.y = y
        self.gx = gx
        self.gy = gy

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

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                x = int(self.x + self.turret_size * math.cos(math.radians(self.angle)))
                y = int(self.y + self.turret_size * math.sin(math.radians(self.angle)))
                self.game.muzzle_fx.addParticle(
                    x, y, (1, 1, 1, 1)
                )
                self.game.muzzle_fx.addParticle(
                    t.x + random.randrange(-2, 3),
                    t.y + random.randrange(-2, 3),
                    (0.95, 0.88, 0.7, 0.9)
                )
                r = random.randint(1, 101)
                if r <= self.crit:
                    t.hp -= self.dmg * 1.5
                else:
                    t.hp -= self.dmg
                self.setCD(self.spd)
        return t


class SplashTower(Tower):

    def __init__(self, game, name="Splash Tower", x=None, y=None):
        super(Tower, self).__init__(
            game.textures["tower_splash"],
            batch=game.batches["fg"],
            group=game.fg_group
        )
        self.name = name
        self.game = game
        self.size = game.squaresize
        self.dmg = 20.0
        self.crit = 0
        self.spd = 1.5
        self.cd = False
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.range = int(game.squaresize * 4)
        self.splash_range = game.squaresize * 2
        self.splash_limit = 4
        self.target = None
        self.turret_size = 18
        self.turret_width = 5
        self.turret_color = (0.28, 0.18, 0.16, 1)
        self.gx = x
        self.gy = y
        if x and y:  # If position is supplied, set it
            self.x = x
            self.y = y
        else:  # Sets the tower position to cursor position
            self.x = self.game.cx
            self.y = self.game.cy
        self.selected = False
        self.angle = random.randrange(0, 360)

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                t.hp -= self.dmg
                # Spawns muzzle particle effect
                x = int(self.x + self.turret_size * math.cos(math.radians(self.angle)))
                y = int(self.y + self.turret_size * math.sin(math.radians(self.angle)))
                self.game.muzzle_fx.addParticle(
                    x, y, (1, 1, 1, 1)
                )

                r = self.splash_range / 4
                # Spawns particle effects on mobs
                anim = animation.Animation(
                    self.game, self.game.anim["pang01"], t.x, t.y
                )
                i = 0
                while i < 5:
                    x = t.x + random.randrange(-r / 2, r / 2)
                    y = t.y + random.randrange(-r / 2, r / 2)
                    self.game.smoke_fx.addParticle(
                        x, y, (0.60, 0.57, 0.55, 0.5)
                    )
                    i += 1
                i = 0
                while i < 5:
                    x = t.x + random.randrange(-r, r)
                    y = t.y + random.randrange(-r, r)
                    self.game.smoke_fx.addParticle(
                        x, y, (0.80, 0.77, 0.75, 0.7)
                    )
                    i += 1
                count = 0
                for m in self.game.mobs:
                    if count >= self.splash_limit:
                        break
                    if not m.id == t.id:
                        if get_dist(t.rx, t.ry, m.x, m.y) <= self.splash_range:
                            m.hp -= self.dmg
                            if m.hp <= 0:
                                m.state = "dead"

                            x = m.x + random.randrange(-5, 6)
                            y = m.y + random.randrange(-4, 5)
                            self.game.smoke_fx.addParticle(
                                x, y, (0.65, 0.60, 0.50, 0.7)
                            )
                            count += 1
                self.setCD(self.spd)


class PoisonTower(Tower):

    def __init__(self, game, name="Poison Tower", x=None, y=None):
        super(Tower, self).__init__(
            game.textures["tower_poison"],
            batch=game.batches["fg"],
            group=game.fg_group
        )
        self.name = name
        self.game = game
        self.size = game.squaresize
        self.dmg = 8.0
        self.crit = 10
        self.spd = 0.8
        self.slow = 30
        self.slow_time = self.spd
        self.cd = False
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.range = int(game.squaresize * 4.5)
        self.target = None
        self.turret_size = 14
        self.turret_width = 2
        self.turret_color = (0.45, 0.65, 0.55, 1)
        self.gx = x
        self.gy = y
        if x and y:  # If position is supplied, set it
            self.x = x
            self.y = y
        else:  # Sets the tower position to cursor position
            self.x = self.game.cx
            self.y = self.game.cy
        self.selected = False
        self.angle = random.randrange(0, 360)

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                t.hp -= self.dmg
                t.setDebuff("slow", slow=self.slow, time=self.slow_time)
                t.setDebuff("poison", tickdmg=self.dmg//4, time=5.0)
                self.setCD(self.spd)

                # Spawns muzzle particle effect
                x = int(
                    self.x + self.turret_size * math.cos(
                        math.radians(self.angle)
                    )
                )
                y = int(
                    self.y + self.turret_size * math.sin(
                        math.radians(self.angle)
                    )
                )

                self.game.puff_fx.addParticle(
                    x, y, (0.65, 0.9, 0.40, 0.9)
                )

                i = 0
                while i < 5:
                    x = t.x + random.randrange(-4, 5)
                    y = t.y + random.randrange(-4, 5)
                    self.game.puff_fx.addParticle(
                        x, y, (0.55, 1, 0.45, 1)
                    )
                    i += 1

        return t

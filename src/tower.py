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

    def __init__(self, game, name="Default", x=0, y=0):
        super(Tower, self).__init__(
            game.window.textures["tower_wood"],
            batch=game.window.batches["towers"],
            group=game.window.fg_group
        )
        self.name = name
        self.game = game
        self.window = game.window
        self.size = game.squaresize
        self.gx = x
        self.gy = y
        if x and y:  # If position is supplied, set it
            self.x = x
            self.y = y
        else:  # Sets the tower position to cursor position
            self.x = self.game.window.cx
            self.y = self.game.window.cy
        self.turret = Sprite(
            self.window.textures["tower_splash_turret"],
            x=self.x, y=self.y,
            batch=self.window.batches["anim"]
        )
        self.dmg = 4.0
        self.crit = 15  # Percentage chance for a critical strike
        self.spd = 0.6  # Time between attacks in seconds
        self.price = 10   # Build price of tower
        self.cd = False
        self.dmg_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal", "flying"]
        self.range = int(self.size * 3)
        self.target = None
        self.turret_size = 14   # Length of turret, in pixels
        self.selected = False
        self.setAngle()

    def setAngle(self, angle=None):
        if self.turret:
            if not angle:
                self.angle = random.randrange(-10, 10)
            else:
                self.angle = angle
            self.turret.rotation = math.degrees(self.angle) + 90

    def updatePos(self, x, y, gx, gy):
        self.x = x
        self.y = y
        self.gx = gx
        self.gy = gy
        if self.turret:
            self.turret.x = self.x
            self.turret.y = self.y

    def updateOffset(self):
        self.x, self.y = self.window.get_windowpos(self.gx, self.gy)
        if self.turret:
            self.turret.x, self.turret.y = self.x, self.y

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

    def sell(self):
        self.game.gold += int(self.price * 0.75)
        self.batch = None
        self.turret = None
        self.window.userinterface.wipe_context_menu()
        self.game.towers.remove(self)
        self.game.grid.update(new=True)

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                x = int(self.x + self.turret_size * math.cos(-self.angle))
                y = int(self.y + self.turret_size * math.sin(-self.angle))
                self.window.muzzle_fx.addParticle(
                    x, y, (1, 1, 1, 1)
                )
                self.window.muzzle_fx.addParticle(
                    t.x + random.randrange(-2, 3),
                    t.y + random.randrange(-2, 3),
                    (0.85, 0.78, 0.6, 0.9)
                )
                r = random.randint(1, 101)
                if r <= self.crit:
                    t.hp -= self.dmg * 1.5
                    volume = 1.0
                    self.window.crit_fx.addParticle(
                        self.x,
                        self.y,
                        (0.9, 0.3, 0.10, 0.9),
                        velocity=(
                            0,
                            24,
                            0
                        )

                    )
                else:
                    volume = 0.5
                    t.hp -= self.dmg

                self.setCD(self.spd)

                self.window.play_sfx("bang1", volume)   # play sound

    def upgrade(self):
        if self.game.gold >= self.price // 2:
            self.spd *= 0.80
            self.dmg = int(self.dmg * 1.25)
            self.game.gold -= self.price // 2
            self.price = int(self.price * 1.5)


class SplashTower(Tower):

    def __init__(self, game, name="Splash Tower", x=0, y=0):
        super(Tower, self).__init__(
            game.window.textures["tower_splash"],
            batch=game.window.batches["towers"],
            group=game.window.fg_group
        )
        self.name = name
        self.game = game
        self.window = game.window
        self.size = game.squaresize
        self.gx = x
        self.gy = y
        if x and y:  # If position is supplied, set it
            self.x = x
            self.y = y
        else:  # Sets the tower position to cursor position
            self.x = self.window.cx
            self.y = self.window.cy
        self.dmg = 15.0
        self.crit = 0
        self.spd = 2.0
        self.cd = False
        self.price = 40
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal"]
        self.range = int(game.squaresize * 2.5)
        self.splash_range = game.squaresize
        self.turret = Sprite(
            self.window.textures["tower_splash_turret"],
            x=self.x, y=self.y,
            batch=self.window.batches["anim"]
        )
        self.splash_limit = 6
        self.target = None
        self.turret_size = 18
        self.selected = False
        self.setAngle()

    def upgrade(self):
        if self.game.gold >= self.price // 2:
            self.dmg = int(self.dmg * 1.30)
            self.range = int(self.range * 1.05)
            self.splash_range = int(self.splash_range * 1.1)
            self.game.gold -= self.price // 2
            self.price += self.price // 2

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                self.window.play_sfx("bang2")
                t.hp -= self.dmg
                # Spawns muzzle particle effect
                x = int(self.x + self.turret_size * math.cos(-self.angle))
                y = int(self.y + self.turret_size * math.sin(-self.angle))
                self.window.muzzle_fx.addParticle(
                    x, y, (1, 1, 1, 1)
                )

                r = self.splash_range / 4
                # Spawns particle effects on mobs
                anim = animation.Animation(
                    self.window, self.window.anim["pang01"], t.x, t.y
                )
                i = 0
                while i < 5:
                    x = t.x + random.randrange(-r / 2, r / 2)
                    y = t.y + random.randrange(-r / 2, r / 2)
                    self.window.smoke_fx.addParticle(
                        x, y, (0.70, 0.67, 0.65, 0.4)
                    )
                    i += 1
                i = 0
                while i < 5:
                    x = t.x + random.randrange(-r, r)
                    y = t.y + random.randrange(-r, r)
                    self.window.smoke_fx.addParticle(
                        x, y, (0.80, 0.77, 0.75, 0.5)
                    )
                    i += 1
                count = 0
                for m in self.game.mobs:
                    if count >= self.splash_limit:
                        break
                    if not m.id == t.id:
                        dist = get_dist(t.rx, t.ry, m.x, m.y)
                        if dist <= self.splash_range:
                            dmg = (dist / self.splash_range) * self.dmg
                            m.hp -= dmg
                            if m.hp <= 0:
                                m.state = "dead"

                            x = m.x + random.randrange(-5, 6)
                            y = m.y + random.randrange(-4, 5)
                            self.window.smoke_fx.addParticle(
                                x, y, (0.75, 0.70, 0.60, 0.5)
                            )
                            count += 1
                self.setCD(self.spd)


class PoisonTower(Tower):

    def __init__(self, game, name="Poison Tower", x=0, y=0):
        super(Tower, self).__init__(
            game.window.textures["tower_poison"],
            batch=game.window.batches["towers"],
            group=game.window.fg_group
        )
        self.name = name
        self.game = game
        self.size = game.squaresize
        self.window = game.window
        self.dmg = 7.0
        self.crit = 10
        self.spd = 1.4
        self.slow = 30
        self.slow_time = 1.0
        self.cd = False
        self.price = 25
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal", "flying"]
        self.range = int(game.squaresize * 4.5)
        self.target = None
        self.turret_size = 14
        self.gx = x
        self.gy = y
        if x and y:  # If position is supplied, set it
            self.x = x
            self.y = y
        else:  # Sets the tower position to cursor position
            self.x = self.window.cx
            self.y = self.window.cy
        self.turret = Sprite(
            self.window.textures["tower_poison_turret"],
            x=self.x, y=self.y,
            batch=self.window.batches["anim"]
        )
        self.selected = False
        self.setAngle()

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                r = random.randint(1, 101)
                if r <= self.crit:
                    t.hp -= self.dmg * 1.5
                    volume = 1.0
                    self.window.crit_fx.addParticle(
                        self.x,
                        self.y,
                        (0.9, 0.3, 0.10, 0.9),
                        velocity=(
                            0,
                            24,
                            0
                        )

                    )
                else:
                    volume = 0.6
                    t.hp -= self.dmg

                self.setCD(self.spd)

                if t.hp <= 0:
                    t.state = "dead"
                else:
                    t.setDebuff("slow", slow=self.slow, time=self.slow_time)
                    print("Slowing for {0} seconds".format(self.slow_time))
                    t.setDebuff("poison", tickdmg=self.dmg//4, time=5.0)

                self.setCD(self.spd)

                # Spawns muzzle particle effect
                x = int(self.x + self.turret_size * math.cos(-self.angle))
                y = int(self.y + self.turret_size * math.sin(-self.angle))

                self.window.puff_fx.addParticle(
                    x, y, (0.65, 0.9, 0.40, 0.9)
                )

                i = 0
                while i < 5:
                    x = t.x + random.randrange(-4, 5)
                    y = t.y + random.randrange(-4, 5)
                    self.window.puff_fx.addParticle(
                        x, y, (0.45, 0.8, 0.35, 1)
                    )
                    i += 1

                self.window.play_sfx("dart", volume)


    def upgrade(self):
        if self.game.gold >= self.price // 2:
            self.dmg = int(self.dmg * 1.25)
            self.slow = int(self.slow * 1.1)
            self.slow_time = self.slow_time * 1.1
            self.spd *= 0.90
            self.game.gold -= self.price // 2
            self.price += self.price // 2


class ChainTower(Tower):

    def __init__(self, game, name="Chain Tower", x=0, y=0):
        super(Tower, self).__init__(
            game.window.textures["tower_chain"],
            batch=game.window.batches["towers"],
            group=game.window.fg_group
        )
        self.name = name
        self.game = game
        self.size = game.squaresize
        self.window = game.window
        self.dmg = 32.0
        self.crit = 0
        self.spd = 3.5
        self.stun_time = 1.5
        self.cd = False
        self.price = 90
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal", "flying"]
        self.range = int(game.squaresize * 3.5)
        self.target = None
        self.turret_size = 14
        self.gx = x
        self.gy = y
        if x and y:  # If position is supplied, set it
            self.x = x
            self.y = y
        else:  # Sets the tower position to cursor position
            self.x = self.window.cx
            self.y = self.window.cy
        self.turret = None
        self.selected = False

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                volume = 0.6
                t.hp -= self.dmg

                self.setCD(self.spd)

                if t.hp <= 0:
                    t.state = "dead"
                else:
                    t.setDebuff("stun", time=self.stun_time)

                self.setCD(self.spd)

                i = 0
                while i < 4:
                    x = t.x + random.randrange(-6, 6)
                    y = t.y + random.randrange(-6, 6)
                    self.window.smoke_fx.addParticle(
                        x, y, (0.7, 0.8, 1.0, 0.7)
                    )
                    i += 1
                self.window.smoke_fx.addParticle(
                    t.x, t.y, (0.5, 0.5, 1.0, 0.9)
                )
                while i < 3:
                    x = t.x + random.randrange(-6, 6)
                    y = t.y
                    self.window.puff_fx.addParticle(
                        x, y, (0.4, 0.6, 1.0, 1.0)
                    )
                    i += 1

                self.window.play_sfx("pluck", volume)

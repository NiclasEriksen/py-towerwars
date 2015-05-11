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
        self.turret = Sprite(
            game.window.textures["tower_wood_turret"],
            x=self.x, y=self.y,
            batch=game.window.batches["anim"]
        )
        self.dmg = 4.0
        self.crit = 15  # Percentage chance for a critical strike
        self.spd = 0.6  # Time between attacks in seconds
        self.price = 10   # Build price of tower
        self.dmg_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal", "flying"]
        self.range = int(game.squaresize * 3)
        self.turret_size = 14   # Length of turret, in pixels

        self.place(game, name, x, y)

    def place(self, game, name, x, y):
        self.name = name
        self.game = game
        self.size = game.squaresize
        self.cd = False
        self.target = None
        self.selected = False
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
        if self.turret:
            self.setAngle()


    def setAngle(self, angle=None):
        if self.turret:
            if not angle:
                self.angle = random.randrange(-10, 10)
            else:
                self.angle = angle
            self.turret.rotation = math.degrees(self.angle) + 90

    def getTarget(self):
        for m in self.game.mobs:
            if(m.move_type in self.target_types):
                dist = get_dist(m.x, m.y, self.x, self.y)
                if dist <= self.range:
                    self.target = m
                    break

    def updateTarget(self):
        dist = get_dist(self.target.x, self.target.y, self.x, self.y)
        if dist > self.range:
            self.target = None

        if self.target not in self.game.mobs:
            self.target = None

        if self.target:
            if self.target.state == "alive":
                if self.turret:
                    rads = get_angle(
                        self.x, self.y, self.target.x, self.target.y
                    )
                    self.setAngle(rads)
                self.doDamage(self.target)  # Do damage
            if self.target.state == "dead":
                self.target = None

    def updatePos(self, x, y, gx, gy):
        self.x = x
        self.y = y
        self.gx = gx
        self.gy = gy
        if self.turret:
            self.turret.x = self.x
            self.turret.y = self.y

    def updateOffset(self):
        self.x, self.y = self.window.getWindowPos(self.gx, self.gy)
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
        if self.game.active_tower == self:
            self.game.active_tower = None
        if self.game.selected_mouse == self:
            self.game.selected_mouse = None
        if self.game.mouse_drag_tower == self:
            self.game.mouse_drag_tower = None
        self.game.towers.remove(self)
        self.game.grid.update(new="update")

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

                self.window.playSFX("bang1", volume)   # play sound

    def pay_upgrade(self):
        if self.game.debug:
            self.price = int(self.price * 1.5)
            return True
        if self.game.gold >= self.price // 2:
            self.game.gold -= self.price // 2
            self.price = int(self.price * 1.5)
            return True
        else:
            return False

    def upgrade(self):
        if self.pay_upgrade():  # Try to pay for upgrade
            self.spd *= 0.90
            self.crit *= 1.1
            self.dmg = int(self.dmg * 1.30)
            self.range = int(self.range * 1.05)


class SplashTower(Tower):

    def __init__(self, game, name="Splash Tower", x=0, y=0):
        super(Tower, self).__init__(
            game.window.textures["tower_splash"],
            batch=game.window.batches["towers"],
            group=game.window.fg_group
        )
        self.dmg = 16.0
        self.crit = 0
        self.spd = 1.8
        self.price = 40
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal"]
        self.range = int(game.squaresize * 2.5)
        self.splash_range = game.squaresize
        self.turret = Sprite(
            game.window.textures["tower_splash_turret"],
            x=x, y=y,
            batch=game.window.batches["anim"]
        )
        self.splash_limit = 3
        self.turret_size = 18

        self.place(game, name, x, y)


    def upgrade(self):
        if self.pay_upgrade():
            self.dmg = int(self.dmg * 1.40)
            self.splash_limit += 1
            self.splash_range = int(self.splash_range * 1.1)

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                self.window.playSFX("bang2")
                t.hp -= self.dmg
                # Spawns muzzle particle effect
                x = int(self.x + self.turret_size * math.cos(-self.angle))
                y = int(self.y + self.turret_size * math.sin(-self.angle))
                self.window.muzzle_fx.addParticle(
                    x, y, (1, 1, 1, 1)
                )

                r = self.splash_range // 2
                # Spawns particle effects on mobs
                animation.Animation(
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
                            animation.Animation(
                                self.window,
                                self.window.anim["pang01"],
                                m.x, m.y
                            )
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
        self.dmg = 7.0
        self.crit = 10
        self.spd = 1.4
        self.slow = 30
        self.slow_time = 1.0
        self.price = 25
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal", "flying"]
        self.range = int(game.squaresize * 4.5)
        self.turret_size = 14
        self.turret = Sprite(
            game.window.textures["tower_poison_turret"],
            x=x, y=y,
            batch=game.window.batches["anim"]
        )

        self.place(game, name, x, y)


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

                self.window.playSFX("dart", volume)

    def upgrade(self):
        if self.pay_upgrade():
            self.dmg = int(self.dmg * 1.25)
            if self.slow < 85:
                self.slow = int(self.slow * 1.1)
            else:
                self.spd *= 0.95
            self.slow_time = self.slow_time * 1.1
            self.spd *= 0.90


class ChainTower(Tower):

    def __init__(self, game, name="Chain Tower", x=0, y=0):
        super(Tower, self).__init__(
            game.window.textures["tower_chain"],
            batch=game.window.batches["towers"],
            group=game.window.fg_group
        )
        self.dmg = 32.0
        self.crit = 0
        self.spd = 3.5
        self.stun_time = 1.5
        self.price = 70
        self.dmg_type = 1  # 0 Normal, 1 Magic, 2 Chaos
        self.target_types = ["normal", "flying"]
        self.range = int(game.squaresize * 3.5)
        self.turret = None

        self.place(game, name, x, y)

    def upgrade(self):
        if self.pay_upgrade():
            self.spd *= 0.90
            self.dmg = int(self.dmg * 1.25)
            self.stun_time *= 1.1
            self.range = int(self.range * 1.05)

    def doDamage(self, t):
        if t.hp <= 0:
            t.state = "dead"
        else:
            if not self.cd:
                ss = self.game.squaresize
                i = 0
                while i < 8:
                    x = self.x + random.randrange(-ss // 2, ss // 2)
                    y = self.y + random.randrange(-ss // 2, ss // 2)
                    self.window.smoke_fx.addParticle(
                        x, y, (0.8, 0.8, 1.0, 0.7)
                    )
                    if not i // 2:
                        self.window.lightning_fx.addParticle(
                            x, y, (0.7, 0.7, 0.8, 0.8)
                        )
                    i += 1
                volume = 0.6
                t.hp -= self.dmg

                self.setCD(self.spd)

                if t.hp <= 0:
                    t.state = "dead"
                else:
                    t.setDebuff("stun", time=self.stun_time)

                self.setCD(self.spd)

                i = 0
                while i < 3:
                    x = t.x + random.randrange(-6, 6)
                    y = t.y + random.randrange(-6, 6)
                    self.window.lightning_fx.addParticle(
                        x, y, (0.7, 0.8, 0.8, 0.7)
                    )
                    i += 1
                # self.window.smoke_fx.addParticle(
                #     t.x, t.y, (0.5, 0.5, 1.0, 0.9)
                # )
                # while i < 3:
                #     x = t.x + random.randrange(-6, 6)
                #     y = t.y
                #     self.window.lightning_fx.addParticle(
                #         x, y, (0.4, 0.6, 1.0, 1.0)
                #     )
                #     i += 1

                self.window.playSFX("bzzt", volume)

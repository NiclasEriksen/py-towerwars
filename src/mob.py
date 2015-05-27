# import subprocess
from pyglet.sprite import Sprite
from functions import *
from main import logger
import random


class Mob(Sprite):

    """The main mob constructor"""

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1Q"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 14.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.0
        self.bounty = 1    # Gold awarded for killing mob
        self.spawn(game)

    def spawn(self, game):
        self.g = game
        self.debug = game.debug
        self.id = self.g.mob_count
        self.g.mob_count += 1
        s = game.grid.start
        self.x_offset = random.randrange(  # Offset for drawing position
            -self.g.squaresize // 8,
            self.g.squaresize // 8
        )
        self.y_offset = random.randrange(
            -self.g.squaresize // 8,
            self.g.squaresize // 8
        )
        self.x = game.window.getWindowPos(s[0], s[1])[0]
        self.y = game.window.getWindowPos(s[0], s[1])[1]  # Drawing position
        self.rx = self.x
        self.ry = self.y  # Real position, which is used in game logic
        self.state = "alive"
        self.hp_max = self.hp
        self.orig_spd = self.spd
        self.slow_cd = None
        self.lastpoint = None
        self.stall_timer = None
        self.debuff_list = []

        self.currentpoint = s
        self.point = 0
        self.path = False
        if self.move_type == "flying":
            self.path = game.grid.getPath(self.currentpoint, flying=True)
        if not self.path:
            self.path = game.grid.path

        try:
            self.targetpoint = self.path[1]
        except IndexError:
            logger.debug("Targetpoint not found in path, setting it to 0,0!!")
            self.targetpoint = (0, 0)

        logger.debug(
            "Spawning mob ID{2}: {0}hp, {1}spd".format(
                self.hp_max, self.spd, self.id
            )
        )

    def setDebuff(self, d_type, **kwargs):
        debuff = None
        if d_type == "slow":
            slow = kwargs.items()[0][1]
            time = kwargs.items()[1][1]
            debuff = Debuff(self, d_type, time, slow=slow)
        elif d_type == "poison":
            dmg = kwargs.items()[0][1]
            time = kwargs.items()[1][1]
            debuff = Debuff(self, d_type, time, dmg=dmg)
        elif d_type == "stun":
            time = kwargs.items()[0][1]
            debuff = Debuff(self, d_type, time)

        if debuff:
            debuff.update()
            self.debuff_list.append(debuff)
        else:
            logger.debug("Could not set debuff for type {0}".format(d_type))

    def updateOffset(self):
        s = self.currentpoint
        self.x, self.y = self.g.window.getWindowPos(s[0], s[1])
        self.rx, self.ry = self.x, self.y

    def updatePos(self, dt=0):
        if (
            not self.stall_timer and (self not in self.g.pf_queue)
            and self.spd > 0.0
        ):

            points = self.path
            tp = self.targetpoint

            if tp in points and tp in self.g.grid.w_grid:
                targetpos = self.g.window.getWindowPos(tp[0], tp[1])

                if get_dist(targetpos[0], targetpos[1], self.rx, self.ry) < 2:
                    self.lastpoint = self.currentpoint
                    self.currentpoint = self.targetpoint
                    if self.currentpoint == self.g.grid.goal:
                        logger.info("Mob reached goal.")
                        self.state = "reached_goal"
                    else:
                        self.point += 1
                        try:
                            self.targetpoint = points[self.point]
                        except IndexError:
                            self.g.pf_queue.append(self)
                        logger.debug(
                                "Reached pos {0}, new target is {1}".format(
                                    self.currentpoint, self.targetpoint
                                )
                            )

                else:
                    if (self not in self.g.pf_queue):
                        rads = get_angle(
                            self.rx, self.ry,
                            targetpos[0], targetpos[1]
                        )
                        self.rx = self.rx + (self.spd + dt) * math.cos(rads)
                        self.ry = self.ry - (self.spd + dt) * math.sin(rads)
                        self.x = self.rx + self.x_offset
                        self.y = self.ry + self.y_offset

            else:
                if (self not in self.g.pf_queue):
                    logger.debug("Need to recalculate mob route.")
                    self.g.pf_queue.append(self)

    def updateTarget(self):
        if not self.state == "stalled":
            logger.debug("Updating target for mob {0}".format(self.id))
            logger.debug("currentpoint: {0}".format(self.currentpoint))
            logger.debug("target_pos: {0}".format(self.targetpoint))
            logger.debug("point: {0}".format(self.point))

            self.point = 0
            g = self.g.grid
            share = False
            if self.targetpoint in g.path:
                self.path = g.path
                self.point = g.path.index(self.targetpoint)
                try:
                    self.targetpoint = g.path[self.point + 1]
                except IndexError:
                    logger.debug("Target point out of range, panick!")
                    self.targetpoint = g.goal
                share = True

            else:
                genpath = True
                share = True
                for p in g.path:
                    if (
                        abs(self.targetpoint[0] - p[0]) <= 1 and
                        abs(self.targetpoint[1] - p[1]) <= 1
                    ):
                        if self.targetpoint in get_diagonal(
                            g.w_grid, p[0], p[1]
                        ):
                            genpath = False
                            share = True
                            self.targetpoint = p
                            break
                        elif (
                            self.targetpoint in get_neighbors(
                                g.w_grid, p[0], p[1]
                            )
                        ):
                            genpath = False
                            share = True
                            self.targetpoint = p
                            break

                if genpath:
                    logger.debug(
                        "Mob {0} had to generate new path.".format(self.id)
                    )
                    newpath = g.getPath(self.currentpoint)

                    if newpath:
                        self.path = newpath
                        if len(newpath) > 1:
                            self.targetpoint = newpath[1]
                        else:
                            self.targetpoint = newpath[0]

                    # if pathfinding is not successfull, stall for a second
                    else:
                        logger.debug("Mob is stalling!")
                        self.state = "stalled"
                        self.stall_timer = self.g.window.fps * 2

                else:
                    logger.debug(
                        "New path was nearby, mob {0} rejoined it.".format(
                            self.id
                        )
                    )
                    self.path = g.path
                    self.point = g.path.index(self.targetpoint) - 1

            # Shares path if mobs nearby is awaiting update
            if share and not self.state == "stalled":
                for m in self.g.pf_queue:
                    if m.id != self.id:
                        if m.currentpoint == self.currentpoint:
                            m.point = self.point
                            m.targetpoint = self.targetpoint
                            m.path = self.path
                            self.g.pf_queue.remove(m)
                            logger.debug("Shared path with nearby mob.")

    def kill(self):
        logger.debug("Mob {0} died at x:{1}, y:{2}".format(
                self.id, self.x, self.y
            )
        )
        i = 0
        while i < 3:    # Spawn three blood splats
                    x = self.x + random.randrange(-8, 8)
                    y = self.y + random.randrange(-8, 8)
                    self.g.window.blood_fx.addParticle(
                        x, y, (1, 0.1, 0.1, 1)
                    )
                    i += 1
        self.debuff_list = []
        if self in self.g.pf_queue:
            self.g.pf_queue.remove(self)
        self.g.gold += self.bounty
        self.g.mobs.remove(self)
        self.g.window.playSFX("splat", 0.7)

    def updateState(self):
        self.debug = self.g.debug

        if self.state == "dead":
            self.kill()
        elif self.state == "reached_goal":
            logger.info("You are leaking!")
            if self in self.g.pf_queue:
                self.g.pf_queue.remove(self)
            self.debuff_list = []
            self.g.mobs.remove(self)
            self.g.leaking()
        elif self.state == "stalled":
            if self.stall_timer > 0:
                self.stall_timer -= 1
            else:
                self.stall_timer = None
                self.state = "alive"
                self.updateTarget()
        else:   # If none of the states apply
            slowed, stunned = False, False
            for d in self.debuff_list:
                if d.d_type == "slow":
                    slowed = True
                elif d.d_type == "stun":
                    stunned = True
                d.update()
            if stunned:
                self.speed = 0.0
            elif not slowed:
                self.spd = self.orig_spd


class Mob1W(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1W"],
            batch=game.window.batches["mobs"]
        )

        self.variant = variant
        self.move_type = "normal"
        self.hp = 35.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.9
        self.bounty = 3

        self.spawn(game)


class Mob1E(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1E"],
            batch=game.window.batches["mobs"]
        )

        self.move_type = "normal"
        self.variant = variant
        self.hp = 180.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.6
        self.bounty = 10

        self.spawn(game)


class Mob1R(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1R"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 80.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.8
        self.bounty = 10

        self.spawn(game)


class Mob1A(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1A"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 300.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.9
        self.bounty = 18

        self.spawn(game)


class Mob1S(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1S"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 300.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.25
        self.bounty = 20

        self.spawn(game)


class Mob1D(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1D"],
            batch=game.window.batches["mobs"]
        )
        self.state = "alive"
        self.move_type = "normal"
        self.variant = variant
        self.hp = 400.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.0
        self.bounty = 25

        self.spawn(game)


class Mob1F(Mob):

    """Flying mob"""

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1F"],
            batch=game.window.batches["flying_mobs"]
        )
        # Adds this mob to the batch with towers
        self.move_type = "flying"
        self.variant = variant
        self.hp = 120.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.9
        self.bounty = 12

        self.spawn(game)

    def updatePos(self, dt=0):
        if not self.stall_timer and (self not in self.g.pf_queue):
            points = self.path
            tp = self.targetpoint

            if tp in points and tp in self.g.grid.fullgrid:
                targetpos = self.g.window.getWindowPos(tp[0], tp[1])

                if get_dist(targetpos[0], targetpos[1], self.rx, self.ry) < 2:
                    self.lastpoint = self.currentpoint
                    self.currentpoint = self.targetpoint
                    if self.currentpoint == self.g.grid.goal:
                        logger.debug("Mob reached goal.")
                        self.state = "reached_goal"
                    else:
                        self.point += 1
                        self.targetpoint = points[self.point]
                        logger.debug(
                            "Reached pos {0}, new target is {1}".format(
                                self.currentpoint, self.targetpoint
                            )
                        )

                else:
                    if (self not in self.g.pf_queue):
                        rads = get_angle(
                            self.rx, self.ry,
                            targetpos[0], targetpos[1]
                        )
                        self.rx = self.rx + (self.spd + dt) * math.cos(rads)
                        self.ry = self.ry - (self.spd + dt) * math.sin(rads)
                        self.x = self.rx + self.x_offset
                        self.y = self.ry + self.y_offset

        elif (self in self.g.pf_queue):
            self.g.pf_queue.remove(self)    # Never calculate path for flying

    def updateTarget(self):
        if not self.state == "stalled":
            logger.debug("Updating target for flying mob.")
            self.point = 0
            if self.targetpoint in self.path:
                self.point = self.path.index(self.targetpoint)
                try:
                    self.targetpoint = self.path[self.point + 1]
                except IndexError:
                    logger.debug("Target point out of range, panick!")
                    self.targetpoint = g.goal

            else:
                pass


class Mob1Z(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1Z"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 900.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.5
        self.bounty = 35

        self.spawn(game)


class Mob1X(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1X"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 800.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.8
        self.bounty = 40

        self.spawn(game)


class Mob1C(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1C"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 900.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.0
        self.bounty = 50

        self.spawn(game)


class Mob1V(Mob):

    def __init__(self, game, variant="YAY", debug=False):
        super(Mob, self).__init__(
            game.window.textures["mob1V"],
            batch=game.window.batches["mobs"]
        )
        self.move_type = "normal"
        self.variant = variant
        self.hp = 2000.0
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.5
        self.bounty = 75

        self.spawn(game)


class Debuff:

    def __init__(self, owner, d_type, time, **kwargs):
        self.owner = owner
        self.d_type = d_type
        self.time = time * self.owner.g.window.fps
        if self.d_type == "slow":
            self.slow = kwargs.items()[0][1]
        elif self.d_type == "poison":
            self.dmg = kwargs.items()[0][1]
        elif self.d_type == "stun":
            pass

    def update(self):
        if self.time > 0:
            self.doEffect()
            self.time -= 1
        else:
            self.owner.spd = self.owner.orig_spd
            self.owner.debuff_list.remove(self)

    def doEffect(self):
        if self.d_type == "slow":
            newspeed = ((100 - self.slow) * self.owner.orig_spd / 100.0)
            if newspeed <= self.owner.spd:
                if newspeed < 0.0:
                    newspeed = 0.0
                self.owner.spd = newspeed
        elif self.d_type == "poison":
            if self.time % self.owner.g.window.fps == 0:
                if self.owner.hp > 0:
                    self.owner.hp -= self.dmg
                    self.owner.g.window.puff_fx.addParticle(
                        self.owner.x + random.randrange(-8, 9),
                        self.owner.y + random.randrange(-6, 7),
                        (0.55, 1, 0.45, 0.5)
                    )
                    self.owner.g.window.skull_fx.addParticle(
                        self.owner.x + random.randrange(0, 12),
                        self.owner.y + random.randrange(0, 12),
                        (0.10, 0.3, 0.10, 0.8),
                        velocity=(
                            random.randrange(-6, 6),
                            random.randrange(8, 24),
                            0
                        )

                    )
                else:
                    self.owner.state = "dead"

        elif self.d_type == "stun":
            if self.time % self.owner.g.window.fps // 2 == 0:
                self.owner.g.window.lightning_fx.addParticle(
                            self.owner.x, self.owner.y, (0.7, 0.8, 0.8, 0.7)
                        )
            self.owner.spd = 0.0

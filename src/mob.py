import subprocess
import pypf
from pyglet.sprite import Sprite
from functions import *
import animation
import random
from lepton import Particle

n_particle = Particle(
    velocity=(1,1,0), 
    color=(0.55 ,0.50, 0.45, 0.5)
)

class Mob(Sprite):

    """The main mob constructor"""

    def __init__(self, game, variant, debug=False):
        super(Mob, self).__init__(
            game.textures["mob1Q"],
            batch=game.batches["mobs"]
        )
        self.g = game
        self.id = self.g.mob_count
        self.g.mob_count += 1
        self.debug = game.debug
        # self.image = mob_img
        s = game.grid.start
        self.x_offset = random.randrange(  # Offset for drawing position
            -self.g.squaresize // 8,
            self.g.squaresize // 8
        )
        self.y_offset = random.randrange(
            -self.g.squaresize // 8,
            self.g.squaresize // 8
        )
        self.x = game.get_windowpos(s[0], s[1])[0]
        self.y = game.get_windowpos(s[0], s[1])[1]  # Drawing position
        self.rx = self.x
        self.ry = self.y  # Real position, which is used in game logic
        self.currentpoint = s
        self.targetpoint = s
        self.lastpoint = None
        self.state = "alive"
        self.variant = variant
        self.hp = 100.0
        self.hp_max = self.hp
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 1.0
        self.debuff_list = []
        self.slow_cd = None
        self.orig_spd = self.spd
        self.stall_timer = None
        self.point = 0
        self.path = game.grid.path
        self.debug = debug
        if self.debug:
            print("Spawning mob!")

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

        if debuff:
            debuff.update()
            self.debuff_list.append(debuff)
        elif self.debug:
            print("Could not set debuff for type {0}".format(d_type))



    def updatePos(self):
        if not self.stall_timer or not self in self.g.pf_queue:

            points = self.path
            tp = self.targetpoint

            if tp in points and tp in self.g.grid.grid:
                targetpos = self.g.get_windowpos(tp[0], tp[1])

                if get_dist(targetpos[0], targetpos[1], self.rx, self.ry) < 2:
                    self.lastpoint = self.currentpoint
                    self.currentpoint = self.targetpoint
                    if self.currentpoint == self.g.grid.goal:
                        if self.debug:
                            print("Mob reached goal.")
                        self.state = "dead"
                    else:
                        self.point += 1
                        try:
                            self.targetpoint = points[self.point]
                        except IndexError:
                            self.g.pf_queue.append(self)
                        if self.debug:
                            print("Reached pos {0}, new target_pos is {1}".format(
                                self.currentpoint, self.targetpoint))

                else:
                    if not self in self.g.pf_queue:
                        rads = get_angle(
                            self.rx, self.ry,
                            targetpos[0], targetpos[1]
                        )
                        self.rx = self.rx + self.spd * math.cos(rads)
                        self.ry = self.ry - self.spd * math.sin(rads)
                        self.x = self.rx + self.x_offset
                        self.y = self.ry + self.y_offset

            else:
                if not self in self.g.pf_queue:
                    if self.debug:
                        print("Need to recalculate mob route.")
                    self.g.pf_queue.append(self)

    def updateTarget(self):
        if self.debug:
            print("Updating target for mob.")
            print("currentpoint: {0}".format(self.currentpoint))
            print("target_pos: {0}".format(self.targetpoint))
            print("point: {0}".format(self.point))

        self.point = 0
        g = self.g.grid
        share = False
        if self.targetpoint in g.path:
            self.path = g.path
            self.point = g.path.index(self.targetpoint)
            try:
                self.targetpoint = g.path[self.point + 1]
            except IndexError:
                if self.debug:
                    print("Target point out of range, panick!")
                self.targetpoint = g.goal
            share = True

        else:
            genpath = True
            share = True
            for p in g.path:
                if abs(self.targetpoint[0] - p[0]) <= 1 and \
                abs(self.targetpoint[1] - p[1]) <= 1:
                    if self.targetpoint in get_diagonal(g.grid, p[0], p[1]):
                        genpath = False
                        share = True
                        self.targetpoint = p
                        break
                    elif self.targetpoint in get_neighbors(g.grid, p[0], p[1]):
                        genpath = False
                        share = True
                        self.targetpoint = p
                        break

            if genpath:
                if self.debug:
                    print("Mob {0} had to generate a new path.".format(self.id))
                newpath = g.getPath(self.currentpoint)

                if newpath:
                    self.path = newpath
                    self.state = "alive"
                    if len(newpath) > 1:
                        self.targetpoint = newpath[1]
                    else:
                        self.targetpoint = newpath[0]

                    ### Shares path if mobs nearby also is waiting for update ###

                # if pathfinding is not successfull, stall for a second
                else:
                    print("Mob is stalling!")
                    self.state == "stalled"

            else:
                if self.debug:
                    print(
                        "New path was nearby, mob {0} rejoined it.".format(
                            self.id)
                    )
                self.path = g.path
                self.point = g.path.index(self.targetpoint) - 1

        if share:
            for m in self.g.pf_queue:
                if m.id != self.id:
                    if m.currentpoint == self.currentpoint:
                        m.point = self.point
                        m.targetpoint = self.targetpoint
                        m.path = self.path
                        # m.x, m.y, m.rx, m.ry = self.x, \
                        #     self.y, self.rx, self.ry
                        m.state = "alive"
                        self.g.pf_queue.remove(m)
                        if self.debug:
                            print("Shared path with nearby mob.")

    def updateState(self):
        self.debug = self.g.debug
        if self.state == "dead":
            anim = animation.Animation(
                self.g, self.g.anim["mob1Qdeath"], self.x, self.y
            )
            if self.debug:
                print("Mob {0} died at x:{1}, y:{2}".format(
                    self.id, self.x, self.y
                ))
            if self in self.g.pf_queue:
                self.g.pf_queue.remove(self)
            self.g.mobs.remove(self)
            self.delete()
        elif self.state == "stalled":
            if not self.stall_timer:
                self.stall_timer = 60
            if self.stall_timer > 0:
                self.stall_timer -= 1
            else:
                self.stall_timer = None
                self.state = "alive"
                self.updateTarget()

        slowed = False
        for d in self.debuff_list:
            if d.d_type == "slow":
                slowed = True
            d.update()

        if not slowed:
            self.spd = self.orig_spd


class Mob1W(Mob):

    def __init__(self, game, variant, debug=False):
        super(Mob, self).__init__(
            game.textures["mob1W"],
            batch=game.batches["mobs"]
        )
        self.g = game
        self.id = self.g.mob_count
        self.g.mob_count += 1
        self.debug = game.debug
        # self.image = mob_img
        s = game.grid.start
        self.x_offset = random.randrange(  # Offset for drawing position
            -self.g.squaresize // 8,
            self.g.squaresize // 8
        )
        self.y_offset = random.randrange(
            -self.g.squaresize // 8,
            self.g.squaresize // 8
        )
        self.x = game.get_windowpos(s[0], s[1])[0]
        self.y = game.get_windowpos(s[0], s[1])[1]  # Drawing position
        self.rx = self.x
        self.ry = self.y  # Real position, which is used in game logic
        self.currentpoint = s
        self.targetpoint = s
        self.lastpoint = None
        self.state = "alive"
        self.variant = variant
        self.hp = 250.0
        self.hp_max = self.hp
        self.def_type = 0  # 0 Normal, 1 Magic, 2 Chaos
        self.spd = 0.9
        self.debuff_list = []
        self.slow_cd = None
        self.orig_spd = self.spd
        self.stall_timer = None
        self.point = 0
        self.path = game.grid.path
        self.debug = debug
        if self.debug:
            print("Spawning mob!")


class Debuff:


    def __init__(self, owner, d_type, time, **kwargs):
        self.owner = owner
        self.d_type = d_type
        self.time = time * 60
        if self.d_type == "slow":
            self.slow = kwargs.items()[0][1]
        elif self.d_type == "poison":
            self.dmg = kwargs.items()[0][1]

    def update(self):
        if self.time > 0:
            self.doEffect()
            self.time -= 1
        else:
            self.owner.debuff_list.remove(self)

    def doEffect(self):
        if self.d_type == "slow":
            newspeed = ((100 - self.slow) * self.owner.orig_spd / 100.0)
            if newspeed <= self.owner.spd:
                self.owner.spd = newspeed
        elif self.d_type == "poison":
            if self.time % 60 == 0:
                if self.owner.hp > 0:
                    self.owner.hp -= self.dmg
                    self.owner.g.puff_fx.addParticle(
                        self.owner.x + random.randrange(-4, 5),
                        self.owner.y + random.randrange(-4, 5),
                        (0.55 ,1, 0.45, 1)
                    )
                else:
                    self.owner.state = "dead"



from lepton import Particle, ParticleGroup, default_system
from lepton.emitter import StaticEmitter
from lepton.renderer import PointRenderer
from lepton.texturizer import SpriteTexturizer
from lepton.controller import Gravity, Lifetime, Movement, Fader, Growth
from pyglet.gl import *


class ParticleCategory:

    def __init__(self, game, t, e,
        x=None, y=None, dx=0, dy=0,
        color=None, size=12
    ):
        self.system = game.particle_system
        self.tex = game.effects
        self.game = game
        self.group = None
        print "Creating new particle category"

        if t == "emitter" and e == "smoke":
            self.createSmokeEmitter(color, size, x, y)
        elif t == "emitter" and e == "puff":
            self.createPuffEmitter(color, size, x, y)
        elif t == "simple" and e == "puff":
            self.createSimplePuff()
        elif t == "simple" and e == "smoke":
            self.createSimpleSmoke()
        elif t == "simple" and e == "pang":
            self.createSimplePang()
        elif t == "simple" and e == "skull":
            self.createSimpleSkull()

    def draw(self):
        self.group.draw()

    def update(self, dt):
        self.group.update(dt)

    def addParticle(self, x, y, color, velocity=(0, 0.6, 0)):
        x, y = float(x), float(y)
        self.group.new(Particle(
            color=color,
            velocity=velocity, position=(x, y, 0))
        )

    def createSimplePuff(self):
        self.group = ParticleGroup(
            controllers=[
                Lifetime(0.6),
                Movement(min_velocity=0.8, max_velocity=16.0, damping=0.20),
                Growth(0.5),
                Fader(
                    fade_in_start=0, start_alpha=0,
                    fade_in_end=0.20, max_alpha=0.8,
                    fade_out_start=0.35, fade_out_end=0.55
                )
            ],
            system=self.system,
            renderer=PointRenderer(
                12,
                SpriteTexturizer(
                    self.tex["puff"].texture.id))
        )

    def createSimpleSmoke(self):
        self.group = ParticleGroup(
            controllers=[
                Lifetime(1.5),
                Movement(min_velocity=0.8, max_velocity=0.9, damping=0.20),
                Growth(0.5),
                Fader(
                    fade_in_start=0, start_alpha=0,
                    fade_in_end=0.15, max_alpha=0.5,
                    fade_out_start=0.25, fade_out_end=1.5
                )
            ],
            system=self.game.particle_system,
            renderer=PointRenderer(
                24,
                SpriteTexturizer(
                    self.tex["smoke"].texture.id))
        )

    def createSimplePang(self):
        self.group = ParticleGroup(
            controllers=[
                Lifetime(0.1),
                Growth(4, damping=0.5),
                Fader(
                    fade_in_start=0, start_alpha=0,
                    fade_in_end=0.10, max_alpha=0.9
                )
            ],
            system=self.game.particle_system,
            renderer=PointRenderer(
                10,
                SpriteTexturizer(
                    self.tex["pang"].texture.id))
        )

    def createSimpleSkull(self):
        self.group = ParticleGroup(
            controllers=[
                Lifetime(0.6),
                Growth(3, damping=0.6),
                Movement(damping=0.95),
                Fader(
                    fade_in_start=0, start_alpha=0,
                    fade_in_end=0.10, max_alpha=1,
                    fade_out_start=0.15, fade_out_end=0.6
                )
            ],
            system=self.game.particle_system,
            renderer=PointRenderer(
                12,
                SpriteTexturizer(
                    self.tex["skull"].texture.id))
        )

    def createSmokeEmitter(self, color, size, x, y, lifetime=6, dx=-1.5, dy=0):
        self.emitter = StaticEmitter(
            rate=5,
            template=Particle(
                position=(x, y, 0),
                color=color),
            deviation=Particle(
                position=(1, 1, 0),
                velocity=(0.6, 0.2, 0),
                color=(0, 0.02, 0, 0),
                age=1))
        self.group = ParticleGroup(
            controllers=[self.emitter, Lifetime(lifetime),
                Gravity((dx, dy, 0)), Movement(),
                Fader(
                    fade_in_start=0, start_alpha=0,
                    fade_in_end=0.20, max_alpha=0.7,
                    fade_out_start=lifetime / 3, fade_out_end=lifetime - 1
                )
            ],
            system=self.system,
            renderer=PointRenderer(32, SpriteTexturizer(
                self.tex["smoke"].texture.id)
            )
        )
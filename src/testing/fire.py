#############################################################################
#
# Copyright (c) 2008 by Casey Duncan and contributors
# All Rights Reserved.
#
# This software is subject to the provisions of the MIT License
# A copy of the license should accompany this distribution.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#
#############################################################################
"""Fire simulation using point sprites"""

__version__ = '$Id: fire.py 219 2009-04-25 19:45:54Z casey.duncan $'

import os, random
from pyglet import image
from pyglet.gl import *

from lepton import Particle, ParticleGroup, default_system
from lepton.renderer import PointRenderer
from lepton.texturizer import SpriteTexturizer, create_point_texture
from lepton.emitter import StaticEmitter
from lepton.domain import Line
from lepton.controller import Gravity, Lifetime, Movement, Fader, ColorBlender, Growth

win = pyglet.window.Window(resizable=True, visible=False)
win.clear()

glEnable(GL_BLEND)
glShadeModel(GL_SMOOTH)
glBlendFunc(GL_SRC_ALPHA,GL_ONE)
glDisable(GL_DEPTH_TEST)

win.set_visible(True)
pyglet.clock.set_fps_limit(None)
template = Particle(
	position=(win.width/2, win.height/2, 0),
	velocity=(0,0,0), 
	color=(0.55 ,0.50, 0.45, 0.5)
)

flame = StaticEmitter(
	template=template,
	rate=20,
	position=Line((win.width/2, win.height/2, 0), (win.width/2, win.height/2, 0)),
	deviation=Particle(position=(0,0,0), velocity=(1,1,0), age=1)
)

default_system.add_global_controller(
	Lifetime(0.5),
	Fader(30),
	Movement(damping=0.95),
	Growth(30),
	Fader(
		fade_in_start=0, start_alpha=0, fade_in_end=0.25, max_alpha=1, 
		fade_out_start=0.25, fade_out_end=0.5
	)
)
pyglet.clock.schedule_interval(default_system.update, (1.0/30.0))

def getgroup():
	group = ParticleGroup(controllers=[flame], 
		renderer=PointRenderer(8, SpriteTexturizer(create_point_texture(16, 3))))
	return group

pgroup = group = ParticleGroup(
		renderer=PointRenderer(8, SpriteTexturizer(create_point_texture(16, 3))))
#  default_system.remove_group(pgroup)

@win.event
def on_draw():
	win.clear()
	glLoadIdentity()
	default_system.draw()
	# pgroup.draw()

@win.event
def on_key_press(symbol, modifiers):
	if symbol == pyglet.window.key.SPACE:
		# group = getgroup()
		pgroup.new(
			template, position=(
				template.position[0] + random.randrange(-5, 6),
				template.position[1] + random.randrange(-5, 6),
				template.position[2]

			)
		)

		# default_system.add_global_controller(
		# 	Lifetime(0.3),
		# 	Movement(), 
		# )

	elif symbol == pyglet.window.key.A:
		default_system.remove_group(pgroup)

if __name__ == '__main__':
	default_system.run_ahead(2, 30)
	pyglet.app.run()

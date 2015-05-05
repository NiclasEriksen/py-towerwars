# py-towerwars
A python implementation of the custom game mode Tower Wars from Warcraft III.

The game is going to be based around PvP play, but with an AI for practice, and involves finding a balance between building defences (towers) and sending creeps to your opponent, which in turn increases your income each round. The game will feature a bunch of different "races", sets of four towers, that players choose from before starting a round. Towers can be upgraded to improve their strength, the cost is relative to the change in stats so the player can choose between building a maze or upgrading without worrying about the cost efficiency.

It's built on [Pyglet](http://www.pyglet.org/), [py-lepton](https://code.google.com/p/py-lepton/) (particle system) and [PyTMX](https://github.com/bitcraft/PyTMX). Most of the assets are free (as in freedom) assets found online.

Here's a list of keyboard shortcuts:

Key | Function
--------------- | ----------------
F11             | Fullscreen
F12             | Debug (G for gold)
F2              | Autospawn random mobs
Space           | Pause
Q, W, E, R      | Mobs tier 1
A, S, D, F      | Mobs tier 2
Z, X, C, V      | Mobs tier 3

Screenshot of early version:

![Screenshot](https://raw.githubusercontent.com/NiclasEriksen/py-towerwars/master/scr.png)
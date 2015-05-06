from pyglet.sprite import Sprite


class Animation(Sprite):

    'The main animation constructor'

    def __init__(self, game, anim, x, y):
        image = anim[0]
        super(Animation, self).__init__(
            image,
            batch=game.batches["anim"],
            group=game.fg_group
        )
        self.x = x
        self.y = y
        self.window = game
        self.image = image
        self.anim = anim
        self.timer = 0
        self.playing = True
        game.animations.append(self)

    def update(self):
        if self.timer < len(self.anim) - 1:
            self.timer += 1
            self.image = self.anim[self.timer]
        else:
            self.playing = False
            self.window.animations.remove(self)

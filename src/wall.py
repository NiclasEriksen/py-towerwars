from pyglet.sprite import Sprite


class Wall(Sprite):

    def __init__(self, game, gx, gy):
        self.game = game
        super(Wall, self).__init__(
            game.textures["wall_stone"],
            batch=game.batches["fg"],
        )
        self.gx = gx
        self.gy = gy
        self.x = game.get_windowpos(gx, gy)[0]
        self.y = game.get_windowpos(gx, gy)[1]

    def updatePos(self):
        self.x, self.y = self.game.get_windowpos(self.gx, self.gy)
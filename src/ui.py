# UI module
from pyglet.sprite import Sprite
from pyglet import gl, graphics, text


class UI():

    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.sprites = []
        self.b_size = self.game.squaresize

    def add_button(self, b_type):
        if b_type == "1":
            x = 20
            y = 20
            texture = "tower_wood"
        if b_type == "2":
            x = 20
            y = 20 + self.b_size
            texture = "tower_splash"
        if b_type == "3":
            x = 20
            y = 20 + self.b_size * 2
            texture = "tower_poison"

        # "tower_splash_turret"

        b_sprite = Sprite(
                        self.game.textures[texture],
                        x=x, y=y,
                        batch=self.game.batches["buttons"],
                        group=self.game.ui_group
                    )

        b_sprite.b_type = b_type
        self.sprites.append(b_sprite)

    def check_mouse(self, pos):
        # Checks if mouse position is on a button
        radius = self.b_size / 2
        for b in self.sprites:
            if pos[0] <= b.x + radius and pos[0] >= b.x - radius:
                if pos[1] <= b.y + radius and pos[1] >= b.y - radius:
                    print "ON BUTTON"
                    return b.b_type
        return False

    def render(self):
        self.game.batches["buttons"].draw()


class MainMenu():

    def __init__(self, game):
        self.game = game
        self.ui = game.userinterface
        self.entries = []

    def add_entry(self, title="No title", action=None):
        b_sprite = Sprite(
                        self.game.textures["wall_stone"],
                        x=self.game.width / 2,
                        y=self.game.height / 2 - (32 * len(self.entries)),
                        batch=self.game.batches["mm_buttons"],
                        group=self.game.ui_group
                    )
        # b_sprite.width, b_sprite.height = 3, 1
        x, y = b_sprite.x, b_sprite.y
        b_sprite.rectangle = (
                x - 64, y - 16,
                x - 64, y + 16,
                x + 64, y + 16,
                x + 64, y - 16,
                )
        b_sprite.action = action
        b_sprite.label = text.Label(
            title, font_name='Times New Roman',
            font_size=18,
            x=x, y=y,
            anchor_x="center", anchor_y="center"
        )
        self.entries.append(b_sprite)

    def check_mouse(self, pos):
        x, y = pos[0], pos[1]
        for e in self.entries:
            if x >= e.rectangle[0] and x <= e.rectangle[4]:
                if y >= e.rectangle[1] and y <= e.rectangle[3]:
                    if e.action == "newgame":
                        self.game.newGame()
                        self.game.mainmenu = None
                    elif e.action == "resume":
                        self.game.paused = False
                        self.game.mainmenu = None
                    elif e.action == "quit":
                        self.game.quit_game()

    def render(self):
        self.game.batches["mm_buttons"].draw()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glColor3f(0.3, 0.3, 0.3, 1)
        for e in self.entries:
            graphics.draw(
                4, gl.GL_QUADS, ('v2i', e.rectangle)
            )
            e.label.draw()

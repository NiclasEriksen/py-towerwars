# UI module
from pyglet.sprite import Sprite
from pyglet import gl, graphics, text


class UI():

    def __init__(self, window):
        self.w = window
        self.buttons = []
        self.texts = []
        self.sprites = []
        # self.b_size = self.game.squaresize
        self.b_size = 32

    def add_text(self, t_type):
        if t_type == "gold":
            x = 20
            y = self.w.height - 25

            label = text.Label(
                str(self.w.game.gold), font_name='UI font',
                font_size=14,
                x=x, y=y,
                anchor_x="center", anchor_y="center",
                color=(255, 255, 155, 255)
            )
            label.t_type = t_type
            label.align = "left"
            self.texts.append(label)

        x = self.w.width - 20
        y = self.w.height - 25

        label = text.Label(
            str(len(self.w.game.mobs)), font_name='UI font',
            font_size=14,
            x=x, y=y,
            anchor_x="center", anchor_y="center",
            color=(255, 155, 255, 255)
        )

        label.t_type = "mob_count"
        label.align = "right"

        self.texts.append(label)

        y = self.w.height - 50

        label = text.Label(
            str(len(self.w.animations)), font_name='UI font',
            font_size=14,
            x=x, y=y,
            anchor_x="center", anchor_y="center",
            color=(255, 155, 255, 255)
        )

        label.t_type = "anim_count"
        label.align = "right"

        self.texts.append(label)

        y = self.w.height - 75

        label = text.Label(
            str(self.w.game.lives), font_name='UI font',
            font_size=14,
            x=x, y=y,
            anchor_x="center", anchor_y="center",
            color=(255, 155, 255, 255)
        )

        label.t_type = "lives"
        label.align = "right"

        self.texts.append(label)

    def add_button(self, b_type):
        if b_type == "1":
            x = 20
            y = 20
            texture = "tower_wood"
        elif b_type == "2":
            x = 20
            y = 20 + self.b_size
            texture = "tower_poison"
        elif b_type == "3":
            x = 20
            y = 20 + self.b_size * 2
            texture = "tower_splash"
        else:
            return False

        b_sprite = Sprite(
                        self.w.textures[texture],
                        x=x, y=y,
                        batch=self.w.batches["buttons"],
                        group=self.w.ui_group
                    )

        b_sprite.active = True
        b_sprite.b_price = self.w.game.available_towers[b_type]
        b_sprite.b_type = b_type
        self.sprites.append(b_sprite)

    def update_buttons(self):
        gold = self.w.game.gold
        for b in self.sprites:
            if not b.b_price <= gold:
                b.opacity = 128
                b.active = False
            else:
                b.opacity = 255
                b.active = True

    def check_mouse(self, pos):
        # Checks if mouse position is on a button
        radius = self.b_size / 2
        for b in self.sprites:
            if b.active:
                if pos[0] <= b.x + radius and pos[0] >= b.x - radius:
                    if pos[1] <= b.y + radius and pos[1] >= b.y - radius:
                        return b.b_type
        return False

    def render(self):
        self.update_buttons()
        self.w.batches["buttons"].draw()
        for t in self.texts:
            if t.t_type == "gold":  # Updates gold count
                t.text = str(self.w.game.gold)
            elif t.t_type == "mob_count":
                t.text = str(len(self.w.game.mobs))
            elif t.t_type == "anim_count":
                t.text = str(len(self.w.animations))
            elif t.t_type == "pf_count":
                t.text = str(len(self.w.game.pf_queue))
            elif t.t_type == "lives":
                t.text = str(self.w.game.lives)
            t.draw()

    def update_offset(self):
        ri = 0      # right counter
        li = 0      # left counter
        for t in self.texts:
            if t.align == "right":
                ri += 1
                t.x = self.w.width - 20
                t.y = self.w.height - 25 * ri
            elif t.align == "left":
                li += 1
                t.x = 20
                t.y = self.w.height - 25 * li

class MainMenu():

    def __init__(self, window):
        self.w = window
        self.ui = window.userinterface
        self.entries = []

    def add_entry(self, title="No title", action=None):
        b_sprite = Sprite(
                        self.w.textures["wall_stone"],
                        x=self.w.width / 2,
                        y=self.w.height / 2 - (32 * len(self.entries)),
                        batch=self.w.batches["mm_buttons"],
                        group=self.w.ui_group
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
            title, font_name='UI font',
            font_size=14,
            x=x, y=y,
            anchor_x="center", anchor_y="center"
        )
        self.entries.append(b_sprite)

    def check_mouse(self, pos):
        x, y = pos[0], pos[1]
        for e in self.entries:
            if x >= e.rectangle[0] and x <= e.rectangle[4]:
                if y >= e.rectangle[1] and y <= e.rectangle[3]:
                    self.w.play_sfx("pluck")
                    if e.action == "newgame":
                        self.w.game.newGame()
                        self.w.mainmenu = None
                    elif e.action == "resume":
                        self.w.game.paused = False
                        self.w.mainmenu = None
                    elif e.action == "quit":
                        self.w.quit_game()

    def render(self):
        self.w.batches["mm_buttons"].draw()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glColor3f(0.3, 0.3, 0.3, 1)
        for e in self.entries:
            graphics.draw(
                4, gl.GL_QUADS, ('v2i', e.rectangle)
            )
            e.label.draw()

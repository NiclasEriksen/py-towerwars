# UI module
from pyglet.sprite import Sprite
from pyglet import gl, graphics, text, image
import copy # to edit images without impacting the original
from functions import *
RES_PATH = "resources/"


class UI():

    def __init__(self, window):
        self.w = window
        self.buttons = []
        self.texts = []
        self.sprites = []
        self.context_sprites = []
        self.active_tower = None
        self.b_size = 32

    def add_text(self, t_type):
        if t_type == "gold":
            x = 32
            y = self.w.height - 16

            label = text.Label(
                str(self.w.game.gold), font_name='Soft Elegance',
                font_size=14,
                x=x, y=y,
                anchor_x="left", anchor_y="center",
                color=(255, 255, 155, 255)
            )
            label.t_type = t_type
            label.align = "left"
            self.texts.append(label)

        x = self.w.width - 20
        y = self.w.height - 25

        label = text.Label(
            str(len(self.w.game.mobs)), font_name='Soft Elegance',
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
            str(len(self.w.animations)), font_name='Soft Elegance',
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
            str(self.w.game.lives), font_name='Visitor TT1 BRK',
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
            category = "tower"
            texture = self.w.textures["tower_wood"]
            active = True
            b_price = self.w.game.available_towers[b_type]
        elif b_type == "2":
            x = 20
            y = 20 + self.b_size
            category = "tower"
            texture = self.w.textures["tower_poison"]
            active = True
            b_price = self.w.game.available_towers[b_type]
        elif b_type == "3":
            x = 20
            y = 20 + self.b_size * 2
            category = "tower"
            texture = self.w.textures["tower_splash"]
            active = True
            b_price = self.w.game.available_towers[b_type]
        elif b_type == "4":
            x = 20
            y = 20 + self.b_size * 3
            category = "tower"
            texture = self.w.textures["tower_chain"]
            active = True
            b_price = self.w.game.available_towers[b_type]
        elif b_type == "gold_icon":
            texture = image.load(RES_PATH + 'ui/gold.png')
            texture = center_image(texture)
            x = texture.width + 2
            y = self.w.height - (texture.height + 2)
            category = "ui"
            active = False
            b_price = False
            b_type = "icon"
        else:
            return False

        b_sprite = Sprite(
                        texture,
                        x=x, y=y,
                        batch=self.w.batches["buttons"],
                        group=self.w.ui_group
                    )

        b_sprite.category = category
        b_sprite.b_type = b_type
        b_sprite.active = active
        b_sprite.b_price = b_price
        self.sprites.append(b_sprite)

    def update_buttons(self):
        gold = self.w.game.gold
        for b in self.sprites:
            if b.category == "tower":
                if not b.b_price <= gold:
                    b.opacity = 80
                    b.active = False
                else:
                    b.opacity = 255
                    b.active = True
        for b in self.context_sprites:
            if b.b_type == "sell":
                b.active = True
            elif b.b_type == "upgrade":
                if isinstance(b, text.Label):
                    b.text = str(b.owner.price // 2)
                    if not b.shadow:
                        if not b.owner.price // 2 <= gold:
                            b.color = (255, 140, 140, 225)
                        else:
                            b.color = (130, 255, 130, 255)
                else:
                    if not b.owner.price // 2 <= gold:
                        b.opacity = 80
                        # b.active = False
                    else:
                        b.opacity = 255
                        # b.active = True


        if self.w.game.active_tower:
            if self.active_tower:
                if self.active_tower == self.w.game.active_tower:
                    pass
                else:
                    self.active_tower = self.w.game.active_tower
                    self.context_menu(self.active_tower)
            else:
                self.active_tower = self.w.game.active_tower
                self.context_menu(self.active_tower)
        else:
            self.wipe_context_menu()
            self.active_tower = None

    def check_mouse(self, pos):
        # Checks if mouse position is on a button
        for b in self.sprites:
            if not isinstance(b, text.Label):
                radius = b.width // 2
                if b.active:
                    if pos[0] <= b.x + radius and pos[0] >= b.x - radius:
                        if pos[1] <= b.y + radius and pos[1] >= b.y - radius:
                            return b.b_type
        for b in self.context_sprites:
            if not isinstance(b, text.Label):
                radius = b.width // 2
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
        for t in self.texts:
            if t.align == "right":
                ri += 1
                t.x = self.w.width - 20
                t.y = self.w.height - 25 * ri
            elif t.align == "left":
                t.y = self.w.height - 16
        for s in self.sprites:
            if s.b_type == "icon":
                s.y = self.w.height - (s.height + 2)
        for s in self.context_sprites:
            s.x = s.owner.x + s.offset[0]
            s.y = s.owner.y + s.offset[1]

    def wipe_context_menu(self):
        for s in self.context_sprites:
            if isinstance(s, text.Label):
                s.delete()
        self.context_sprites = []

    def context_menu(self, obj, action="show"):
        self.wipe_context_menu()
        category = "context"
        texture = image.load(RES_PATH + 'ui/upgrade.png')
        texture = center_image(texture)
        offset =  (
            0.0 - texture.width // 2,
            obj.height // 2 + texture.height // 2
        )
        b_sprite = Sprite(
                texture,
                x=obj.x + offset[0],
                y=obj.y + offset[1],
                batch=self.w.batches["buttons"],
                group=self.w.ui_group
        )

        b_sprite.offset = offset
        b_sprite.active = True
        b_sprite.b_price = obj.price // 2
        if b_sprite.b_price > self.w.game.gold:
            b_sprite.opacity = 80
        b_sprite.b_type = "upgrade"
        b_sprite.category = category
        b_sprite.owner = obj
        self.context_sprites.append(b_sprite)

        size = 10
        offset = (
            0.0 - texture.width // 2 + 1,
            obj.height // 2 + texture.height // 2 + (size * 1.5) - 1
        )
        x = obj.x + offset[0]
        y = obj.y + offset[1]
        label = text.Label(
            str(obj.price // 2), font_name='Visitor TT1 BRK',
            font_size=size,
            x=x,
            y=y,
            batch=self.w.batches["buttons"],
            anchor_x="center", anchor_y="center",
            color=(32, 32, 32, 196)
        )
        label.offset = offset
        label.owner = obj
        label.b_type = "upgrade"
        label.category = category
        label.shadow = True
        self.context_sprites.append(label)

        offset = (
            0.0 - texture.width // 2,
            obj.height // 2 + texture.height // 2 + (size * 1.5)
        )
        x = obj.x + offset[0]
        y = obj.y + offset[1]
        label = text.Label(
            str(obj.price // 2), font_name='Visitor TT1 BRK',
            font_size=size,
            x=x,
            y=y,
            batch=self.w.batches["buttons"],
            anchor_x="center", anchor_y="center",
            color=(130, 255, 130, 255)
        )
        label.offset = offset
        label.owner = obj
        label.b_type = "upgrade"
        label.category = category
        label.shadow = False
        if obj.price // 2 > self.w.game.gold:
            label.color = (255, 140, 140, 225)
        self.context_sprites.append(label)

        texture = image.load(RES_PATH + 'ui/sell.png')
        texture = center_image(texture)
        offset =  (
            texture.width // 2,
            obj.height // 2 + texture.height // 2
        )
        b_sprite = Sprite(
                texture,
                x=obj.x + offset[0],
                y=obj.y + offset[1],
                batch=self.w.batches["buttons"],
                group=self.w.ui_group
        )
        b_sprite.offset = offset
        b_sprite.active = True
        b_sprite.b_price = obj.price
        b_sprite.b_type = "sell"
        b_sprite.category = category
        b_sprite.owner = obj
        self.context_sprites.append(b_sprite)


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
        b_sprite.rectangle = create_rectangle(x, y, 128, 32)
        b_sprite.action = action
        b_sprite.label = text.Label(
            title, font_name='Soft Elegance',
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

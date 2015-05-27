# UI module
from pyglet.sprite import Sprite
from pyglet import gl, graphics, text
from functions import *
from numpy import log2
from main import logger


class UI():

    def __init__(self, window):
        self.w = window
        self.buttons = []
        self.texts = []
        self.sprites = []
        self.context_sprites = []
        self.active_tower = None
        self.b_size = 32

    def addText(self, t_type):
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

    def addButton(self, b_type):
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
            texture = self.w.textures['gold']
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

    def updateButtons(self):
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
                    self.showContextMenu(self.active_tower)
            else:
                self.active_tower = self.w.game.active_tower
                self.showContextMenu(self.active_tower)
        else:
            self.wipeContextMenu()
            self.active_tower = None

    def checkMouse(self, pos):
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
                xrad = b.width // 2
                yrad = b.height // 2
                if b.active:
                    if pos[0] <= b.x + xrad and pos[0] >= b.x - xrad:
                        if pos[1] <= b.y + yrad and pos[1] >= b.y - yrad:
                            return b.b_type
        return False

    def render(self):
        self.updateButtons()
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

    def updateOffset(self):
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

    def wipeContextMenu(self):
        for s in self.context_sprites:
            if isinstance(s, text.Label):
                s.delete()
        self.context_sprites = []

    def showContextMenu(self, obj, action="show"):
        self.wipeContextMenu()
        category = "context"
        texture = self.w.textures['upgrade']
        offset =  (
            -texture.width,
            0
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
            -texture.width - 1,
            texture.width // 2 - 1
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

        size = 10
        offset = (
            0,
            obj.image.height
        )
        x = obj.x + offset[0]
        y = obj.y + offset[1]
        label = text.Label(
            str(int(obj.dmg)), font_name='Visitor TT1 BRK',
            font_size=size,
            x=x,
            y=y,
            batch=self.w.batches["buttons"],
            anchor_x="center", anchor_y="center",
            color=(32, 32, 32, 255)
        )
        label.offset = offset
        label.owner = obj
        label.b_type = "towerinfo"
        label.category = category
        label.shadow = False
        self.context_sprites.append(label)

        offset = (
            -texture.width,
            texture.width // 2
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

        texture = self.w.textures["sell"]
        offset = (
            texture.width,
            0
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
        self.but_h = 32
        self.but_w = 192
        self.max_char = 18
        self.font_clr = (225, 225, 200, 255)
        self.font_a_clr = (128, 128, 128, 255)
        self.spacing = 8
        self.font_size = 12
        self.entries = []
        self.under_mouse = None
        self.active_entry = False
        self.animation_running = False
        self.animation_counter = 0
        self.current_animation = None
        self.header = None

    def addHeader(self, title="No title"):
        label = text.Label(
            title, font_name="Visitor TT1 BRK",
            font_size=self.font_size * 2,
            color=self.font_clr,
            x=self.w.width / 2,
            y=self.w.height - self.font_size * 3,
            batch=self.w.batches["mm_labels"],
            anchor_x="center", anchor_y="center"
        )

        self.header = label

    def addEntry(self, title="No title", action=None, top=False):
        h = self.but_h
        w = self.but_w
        x = self.w.width / 2
        y = (
            self.w.height / 2 - (h * len(self.entries)) +
            self.spacing
        )
        if title == "New Game":
            btn_texture = self.w.textures["button_green_jagged"]
        elif title == "Exit":
            btn_texture = self.w.textures["button_red"]
        else:
            btn_texture = self.w.textures["button_brown"]
        b_sprite = Sprite(
                        btn_texture,
                        x=x,
                        y=y,
                        batch=self.w.batches["mm_buttons"],
                        group=self.w.ui_group,
                    )
        b_sprite.opacity = 150
        # b_sprite.width, b_sprite.height = 3, 1
        b_sprite.rectangle = create_rectangle(x, y, w, h)
        b_sprite.action = action
        b_sprite.label = text.Label(
            title, font_name='Visitor TT1 BRK',
            font_size=self.font_size,
            color=self.font_clr,
            x=x, y=y,
            batch=self.w.batches["mm_labels"],
            anchor_x="center", anchor_y="center"
        )
        b_sprite.label.oldfontsize = b_sprite.label.font_size
        b_sprite.orig_size = self.but_w, self.but_h
        b_sprite.bw, b_sprite.bh = b_sprite.orig_size

        if top:
            self.entries.insert(0, b_sprite)
            self.updateOffset()
        else:
            self.entries.append(b_sprite)
            self.updateOffset()

    def clearEntries(self):
        self.w.batches["mm_labels"] = graphics.Batch()
        self.w.batches["mm_buttons"] = graphics.Batch()
        self.entries = []
        self.header = None

    def checkMouse(self, pos):
        x, y = pos[0], pos[1]
        for e in self.entries:
            if x >= e.rectangle[0] and x <= e.rectangle[4]:
                if y >= e.rectangle[1] and y <= e.rectangle[3]:
                    if not self.active_entry:
                        self.onDown(e)
                        self.active_entry = e
                        return e
                    else:
                        self.onDown(e)
                        return e
        return False

    def getUnderMouse(self, x, y):
        for e in self.entries:
            e.label.font_size = self.font_size
            e.opacity = 150
            if x >= e.rectangle[0] and x <= e.rectangle[4]:
                if y >= e.rectangle[1] and y <= e.rectangle[3]:
                    e.opacity = 255
                    self.under_mouse = e
                    return True
        else:
            if self.under_mouse:
                self.under_mouse.opacity = 150
            self.under_mouse = None
            return False

    def onDown(self, entry):
        # if entry.label:
        #     entry.label.bold = True
        pass

    def onUp(self, entry):
        if entry.label:
            pass
            # entry.label.bold = False
        self.active_entry = False

    def doAction(self, entry):
        self.w.playSFX("click")
        self.onUp(entry)
        e = entry
        if e.action == "newgame":
            self.animateOut()
            self.on_anim_end = e.action
        elif e.action == "selectmap":
            index = self.w.maplist.index(self.w.selected_mapfile)
            if index == len(self.w.maplist) - 1:
                self.w.selected_mapfile = self.w.maplist[0]
            else:
                self.w.selected_mapfile = self.w.maplist[index + 1]

            str_len = len(self.w.selected_mapfile)
            if str_len > self.max_char:
                string = self.w.selected_mapfile[str_len - self.max_char:]
            else:
                string = self.w.selected_mapfile
            e.label.text = string
        elif e.action == "resume":
            self.animateOut()
            self.on_anim_end = e.action
        elif e.action == "settings":
            self.animateOut()
            self.on_anim_end = e.action
        elif e.action == "togglesound":
            self.w.sound_enabled = not self.w.sound_enabled
            e.label.text = "Sound: {0}".format(self.w.sound_enabled)
            logger.debug(
                "Toggled sound_enabled to {0}.".format(self.w.sound_enabled)
            )
        elif e.action == "topmenu":
            self.animateOut()
            self.on_anim_end = e.action
        elif e.action == "quit":
            self.animateOut()
            self.on_anim_end = e.action

    def handleAction(self, action):
        if action == "settings":
            self.w.showSettingsMenu()
        elif action == "newgame":
            self.w.game.newGame(self.w.selected_mapfile)
        elif action == "resume":
            self.w.game.paused = False
            self.w.mainmenu = None
        elif action == "topmenu":
            self.w.showMainMenu()
        elif action == "quit":
            self.w.quitGame()

    def animateIn(self):
        if not self.animation_running:
            self.animation_running = True
            self.current_animation = "in"
            self.animation_counter = 30

        if self.animation_counter > 0:
            a = log2(self.animation_counter)*(30/log2(30)) / 30
            for e in self.entries:
                e.label.font_size = e.label.oldfontsize * (1.0 - a)
                e.scale = 1.0 - a
            self.animation_counter -= 8
        else:
            for e in self.entries:
                e.scale = 1.0
                e.label.font_size = e.label.oldfontsize
            self.animation_running = False
            self.current_animation = None
            self.animation_counter = 0

        self.updateOffset()

    def animateOut(self):
        if not self.animation_running:
            self.animation_running = True
            self.current_animation = "out"
            self.animation_counter = 30

        if self.animation_counter > 0:
            a = log2(self.animation_counter)*(30/log2(30)) / 30
            for e in self.entries:
                e.label.font_size = e.label.oldfontsize * a
                e.scale = a
            self.animation_counter -= 6
        else:
            self.animation_running = False
            self.current_animation = None
            self.animation_counter = 0
            if self.on_anim_end:
                self.handleAction(self.on_anim_end)

        self.updateOffset()

    def updateAnimation(self):
        if self.current_animation == "in":
            self.animateIn()
        elif self.current_animation == "out":
            self.animateOut()

    def updateOffset(self):
        count = len(self.entries)
        offset_y = (count * (self.but_h + self.spacing)) // 2
        for e in self.entries:
            x = self.w.width // 2
            y = int(
                self.w.height // 2 + offset_y -
                (self.but_h * self.entries.index(e)) -
                (self.spacing * self.entries.index(e))
            )
            # y -= self.spacing * 10

            # print "self.but_h, self.but_w, x, y = {0} {1} {2} {3}".format(
            #     self.but_h, self.but_w, x, y
            # )
            e.label.x, e.x, e.label.y, e.y = x, x, y, y
            e.rectangle = create_rectangle(x, y, e.bw, e.bh, centered=True)

    def render(self):
        self.updateAnimation()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        self.w.batches["mm_buttons"].draw()
        gl.glColor4f(0.3, 0.3, 0.9, 1)
        self.w.batches["mm_labels"].draw()

import pyxel
import random
import time

W, H = 320, 240

# ───────── RANDOM ACCESS MATCH GAME ─────────
class RandomAccessMatch:
    def __init__(self):
        self.px = 150
        self.py = 150
        self.speed = 2

        self.card_w = 40
        self.card_h = 40
        self.grid_rows = 4
        self.grid_cols = 4

        self.cards = []
        self.flipped = []
        self.revealed = []

        self.can_move = True
        self.flip_timer = None

        self.turns = 0
        self.mistakes = 0

        self.preview_time = None
        self.preview_duration = 2

        self.shapes = [
            ("heart", 14),
            ("square", 11),
            ("circle", 12),
            ("rectangle", 9),
            ("diamond", 6),
            ("oval", 15),
            ("trapezoid", 8),
            ("hexagon", 10)
        ]

        self.prepare_cards()

    def start(self):
        self.flipped = []
        self.revealed = []
        self.can_move = True
        self.flip_timer = None

        self.turns = 0
        self.mistakes = 0

        self.px = W // 2
        self.py = H // 2

        for card in self.cards:
            card["flipped"] = False
            card["flip_progress"] = 1

        self.preview_time = time.time()

    def prepare_cards(self):
        card_shapes = self.shapes * 2
        random.shuffle(card_shapes)

        self.cards = []
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                x = 60 + j * (self.card_w + 5)
                y = 50 + i * (self.card_h + 5)
                shape, col = card_shapes.pop()

                self.cards.append({
                    "x": x,
                    "y": y,
                    "shape": shape,
                    "color": col,
                    "flipped": False,
                    "flip_progress": 1
                })

    def update(self):
        # PREVIEW MODE
        if self.preview_time:
            if time.time() - self.preview_time < self.preview_duration:
                for card in self.cards:
                    card["flipped"] = True
                return
            else:
                for card in self.cards:
                    card["flipped"] = False
                self.preview_time = None

        # MOVEMENT
        if self.can_move:
            if pyxel.btn(pyxel.KEY_LEFT):
                self.px -= self.speed
            if pyxel.btn(pyxel.KEY_RIGHT):
                self.px += self.speed
            if pyxel.btn(pyxel.KEY_UP):
                self.py -= self.speed
            if pyxel.btn(pyxel.KEY_DOWN):
                self.py += self.speed

        self.px = max(5, min(W - 5, self.px))
        self.py = max(5, min(H - 5, self.py))

        # FLIP CARD
        if pyxel.btnp(pyxel.KEY_SPACE):
            for card in self.cards:
                if self.is_on_card(card) and card not in self.flipped + self.revealed:
                    card["flipped"] = True
                    card["flip_progress"] = 0
                    self.flipped.append(card)

                    if len(self.flipped) == 2:
                        self.check_match()

        # LOCK MOVEMENT
        if len(self.flipped) == 2:
            self.can_move = False

        # FLIP BACK TIMER
        if self.flip_timer:
            if time.time() - self.flip_timer > 0.5:
                for card in self.flipped:
                    card["flipped"] = False
                self.flipped = []
                self.flip_timer = None
                self.can_move = True

        # ANIMATION
        for card in self.cards:
            if card["flipped"] and card["flip_progress"] < 1:
                card["flip_progress"] += 0.2

    def is_on_card(self, card):
        return (
            self.px >= card["x"] and self.px <= card["x"] + self.card_w and
            self.py >= card["y"] and self.py <= card["y"] + self.card_h
        )

    def check_match(self):
        a, b = self.flipped
        self.turns += 1

        if a["shape"] == b["shape"]:
            self.revealed += [a, b]
            self.flipped = []
            pyxel.play(0, 0)
            self.can_move = True
        else:
            self.mistakes += 1
            self.flip_timer = time.time()
            pyxel.play(0, 1)

    def draw(self):
        pyxel.cls(0)

        hovered = None
        for card in self.cards:
            if self.is_on_card(card):
                hovered = card

        for card in self.cards:
            if card == hovered:
                pyxel.rectb(card["x"] - 1, card["y"] - 1, self.card_w + 2, self.card_h + 2, 10)

            if card["flipped"] or card in self.revealed:
                scale = card["flip_progress"]
                w = int(self.card_w * scale)
                px = card["x"] + (self.card_w - w) // 2

                pyxel.rect(px, card["y"], w, self.card_h, 7)

                if scale > 0.5:
                    self.draw_shape(card)
            else:
                self.draw_ram(card)

        self.draw_player()

        pyxel.text(5, 5, f"Turns: {self.turns}", 7)
        pyxel.text(5, 15, f"Mistakes: {self.mistakes}", 8)

        if len(self.revealed) == 16:
            pyxel.rect(60, 80, 200, 80, 0)
            pyxel.rectb(60, 80, 200, 80, 7)

            pyxel.text(110, 95, "YOU WIN!", 11)
            pyxel.text(90, 110, f"Turns: {self.turns}", 7)
            pyxel.text(90, 120, f"Mistakes: {self.mistakes}", 8)

        pyxel.text(5, H - 10, "TAB to return", 5)
        pyxel.text(W - 80, H - 10, "ESC to exit", 5)

    def draw_player(self):
        pyxel.rect(self.px - 3, self.py - 6, 6, 6, 4)

    def draw_shape(self, card):
        cx = card["x"] + self.card_w // 2
        cy = card["y"] + self.card_h // 2
        col = card["color"]
        shape = card["shape"]

        if shape == "circle":
            pyxel.circ(cx, cy, 5, col)
        elif shape == "square":
            pyxel.rect(cx - 5, cy - 5, 10, 10, col)
        elif shape == "heart":
            pyxel.tri(cx, cy - 6, cx - 6, cy + 4, cx + 6, cy + 4, col)
        elif shape == "rectangle":
            pyxel.rect(cx - 8, cy - 3, 16, 6, col)
        elif shape == "trapezoid":
            pyxel.tri(cx - 6, cy + 5, cx - 4, cy - 5, cx + 4, cy - 5, col)
            pyxel.tri(cx - 6, cy + 5, cx + 6, cy + 5, cx + 4, cy - 5, col)
        elif shape == "diamond":
            pyxel.tri(cx, cy - 6, cx - 6, cy, cx + 6, cy, col)
            pyxel.tri(cx, cy + 6, cx - 6, cy, cx + 6, cy, col)
        elif shape == "oval":
            pyxel.rect(cx - 2, cy - 6, 4, 12, col)
            pyxel.rect(cx - 6, cy - 2, 12, 4, col)
        elif shape == "hexagon":
            pyxel.rect(cx - 1, cy - 6, 2, 12, col)
            pyxel.rect(cx - 6, cy - 1, 12, 2, col)
            pyxel.rect(cx - 4, cy - 4, 8, 8, col)

    def draw_ram(self, card):
        pyxel.rect(card["x"], card["y"], self.card_w, self.card_h, 2)
        text = "R.A.M."
        tx = card["x"] + (self.card_w - len(text) * 4) // 2
        ty = card["y"] + self.card_h // 2 - 2
        pyxel.text(tx, ty, text, 1)


# ───────── MAIN APP ─────────
class App:
    def __init__(self):
        pyxel.init(W, H, title="Pyxel Port")

        pyxel.sound(0).set("c3e3g3", "p", "7", "s", 5)
        pyxel.sound(1).set("c2", "p", "6", "s", 10)

        self.state = "menu"
        self.games = ["Game 1", "Game 2", "Random Access Match", "Game 4", "Game 5"]
        self.selected = 2

        self.ram_game = RandomAccessMatch()

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.state == "menu":
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.selected = (self.selected + 1) % len(self.games)
            if pyxel.btnp(pyxel.KEY_UP):
                self.selected = (self.selected - 1) % len(self.games)

            if pyxel.btnp(pyxel.KEY_RETURN):
                if self.selected == 2:
                    self.ram_game.start()
                    self.state = "game_ram"

        elif self.state == "game_ram":
            self.ram_game.update()

            if pyxel.btnp(pyxel.KEY_TAB):
                self.state = "menu"
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                pyxel.quit()

    def draw(self):
        pyxel.cls(0)

        if self.state == "menu":
            pyxel.text(120, 40, "PYXEL PORT", 7)

            for i, game in enumerate(self.games):
                y = 100 + i * 12
                prefix = ">" if i == self.selected else " "
                pyxel.text(110, y, prefix + game, 7)

        elif self.state == "game_ram":
            self.ram_game.draw()


App()

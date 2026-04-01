import pyxel
import random
import time

# SCREEN SIZE
W, H = 320, 240

# ───────── RANDOM ACCESS MATCH GAME ─────────
class RandomAccessMatch:
    def __init__(self):
        self.px = 150
        self.py = 150
        self.speed = 2
        self.crouching = False
        self.card_w = 40
        self.card_h = 40
        self.grid_rows = 4
        self.grid_cols = 4
        self.cards = []
        self.flipped = []
        self.revealed = []
        self.can_move = True
        self.congrats_start = None
        self.congrats_flash_count = 0
        self.congrats_show = False

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
        self.congrats_start = None
        self.congrats_flash_count = 0
        self.congrats_show = False
        self.px = W // 2
        self.py = H // 2

        for card in self.cards:
            card["flipped"] = False

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
                    "flipped": False
                })

    def update(self):
        # MOVEMENT
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

        # CROUCH (SPACE)
        if pyxel.btnp(pyxel.KEY_SPACE):
            for card in self.cards:
                if self.is_on_card(card) and card not in self.flipped + self.revealed:
                    card["flipped"] = True
                    self.flipped.append(card)
                    if len(self.flipped) == 2:
                        self.check_match()

        # Flip back logic
        if hasattr(self, "flip_timer") and self.flip_timer:
            if time.time() - self.flip_timer > 0.5:
                for card in self.flipped:
                    card["flipped"] = False
                self.flipped = []
                self.flip_timer = None

        # Win check
        if len(self.revealed) == 16 and not self.congrats_start:
            self.congrats_start = time.time()
            self.congrats_flash_count = 0
            self.congrats_show = True

        # Flash logic
        if self.congrats_start and self.congrats_flash_count < 6:
            if time.time() - self.congrats_start > 0.5:
                self.congrats_show = not self.congrats_show
                self.congrats_start = time.time()
                self.congrats_flash_count += 1
        elif self.congrats_flash_count >= 6:
            self.congrats_show = True

    def is_on_card(self, card):
        return (self.px >= card["x"] and self.px <= card["x"]+self.card_w and
                self.py >= card["y"] and self.py <= card["y"]+self.card_h)

    def check_match(self):
        a, b = self.flipped
        if a["shape"] == b["shape"]:
            self.revealed += [a, b]
            self.flipped = []
        else:
            self.flip_timer = time.time()

    def draw(self):
        pyxel.cls(0)

        for card in self.cards:
            if card["flipped"] or card in self.revealed:
                pyxel.rect(card["x"], card["y"], self.card_w, self.card_h, 7)
                self.draw_shape(card)
            else:
                self.draw_ram(card)

        self.draw_player()

        pyxel.text(5, H-10, "TAB to return", 5)
        esc_text = "ESC to exit"
        pyxel.text(W - len(esc_text)*4 - 5, H-10, esc_text, 5)

        if self.congrats_show:
            msg = "CONGRATS!!"
            pyxel.text((W - len(msg)*8)//2, 20, msg, 3)

    def draw_player(self):
        pyxel.rect(self.px-3, self.py-6, 6, 6, 4)

    def draw_shape(self, card):
        cx = card["x"] + self.card_w // 2
        cy = card["y"] + self.card_h // 2
        col = card["color"]
        shape = card["shape"]

        # 🔵 Circle
        if shape == "circle":
         pyxel.circ(cx, cy, 5, col)

        # 🟩 Square
        elif shape == "square":
            pyxel.rect(cx - 5, cy - 5, 10, 10, col)

        # 🔺 Triangle (used instead of heart for cleaner retro look)
        elif shape == "heart":
         pyxel.tri(cx, cy - 6, cx - 6, cy + 4, cx + 6, cy + 4, col)

     # 🟧 Long Rectangle
        elif shape == "rectangle":
            pyxel.rect(cx - 8, cy - 3, 16, 6, col)

    # 🔴 Trapezoid (square with angled sides)
        elif shape == "trapezoid":
            pyxel.tri(cx - 6, cy + 5, cx - 4, cy - 5, cx + 4, cy - 5, col)
            pyxel.tri(cx - 6, cy + 5, cx + 6, cy + 5, cx + 4, cy - 5, col)

    # 🔷 Diamond (two triangles)
        elif shape == "diamond":
         pyxel.tri(cx, cy - 6, cx - 6, cy, cx + 6, cy, col)
         pyxel.tri(cx, cy + 6, cx - 6, cy, cx + 6, cy, col)

    # 🍑 Thick Plus
        elif shape == "oval":
         pyxel.rect(cx - 2, cy - 6, 4, 12, col)
         pyxel.rect(cx - 6, cy - 2, 12, 4, col)

    # ⭐ Star (simple pixel star)
        elif shape == "hexagon":
         pyxel.rect(cx - 1, cy - 6, 2, 12, col)
         pyxel.rect(cx - 6, cy - 1, 12, 2, col)
         pyxel.rect(cx - 4, cy - 4, 8, 8, col)

         
    # 🔥 UPDATED: SIDEWAYS TEXT
    def draw_ram(self, card):
        pyxel.rect(card["x"], card["y"], self.card_w, self.card_h, 2)

        text = "R.A.M."
        text_width = len(text) * 4

        # center horizontally
        tx = card["x"] + (self.card_w - text_width) // 2
        ty = card["y"] + self.card_h // 2 - 2

        pyxel.text(tx, ty, text, 1)

# ───────── MAIN MENU ─────────
class App:
    def __init__(self):
        pyxel.init(W, H, title="Pyxel Port")

        self.state = "menu"
        self.games = [
            "Game 1",
            "Game 2",
            "Random Access Match",
            "Game 4",
            "Game 5"
        ]
        self.selected = 0

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
                else:
                    self.state = f"game_{self.selected+1}"

        elif self.state == "game_ram":
            self.ram_game.update()

            if pyxel.btnp(pyxel.KEY_TAB):
                self.state = "menu"

            if pyxel.btnp(pyxel.KEY_ESCAPE):
                pyxel.quit()

        elif self.state.startswith("game_"):
            if pyxel.btnp(pyxel.KEY_TAB):
                self.state = "menu"

            if pyxel.btnp(pyxel.KEY_ESCAPE):
                pyxel.quit()

    def draw(self):
        pyxel.cls(0)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game_ram":
            self.ram_game.draw()
        else:
            self.draw_placeholder()

    def draw_menu(self):
        for y in range(H):
            pyxel.line(0, y, W, y, 1 if y < H//2 else 0)

        title = "PYXEL PORT"
        scale = 4
        start_x = (W - len(title)*(3*scale+scale)) // 2

        for i, ch in enumerate(title):
            self.draw_block_char(start_x + i*(3*scale+scale), 40, ch, scale, 8)

        if pyxel.frame_count % 40 < 20:
            text = "INSERT COIN"
            pyxel.text((W - len(text)*4)//2, 95, text, 10)

        pyxel.rect(80, 102, 160, 110, 0)
        pyxel.rectb(80, 102, 160, 110, 7)

        for i, game in enumerate(self.games):
            y = 122 + i*14
            if i == self.selected:
                pyxel.circ(95, y+3, 2, 10)

            pyxel.text(110, y, game, 7)

    def draw_block_char(self, x, y, ch, s, col):
        patterns = {
            "P":["110","101","110","100","100"],
            "Y":["101","101","010","010","010"],
            "X":["101","010","010","010","101"],
            "E":["111","100","110","100","111"],
            "L":["100","100","100","100","111"],
            "O":["111","101","101","101","111"],
            "R":["110","101","110","101","101"],
            "T":["111","010","010","010","010"],
            " ":"000"
        }

        pattern = patterns.get(ch, patterns[" "])

        for row, line in enumerate(pattern):
            for col_i, bit in enumerate(line):
                if bit == "1":
                    pyxel.rect(x + col_i*s, y + row*s, s, s, col)

    def draw_placeholder(self):
        pyxel.cls(0)

        game_index = int(self.state.split("_")[1])
        game_name = self.games[game_index-1]

        msg = f"INSERT {game_name} HERE"
        pyxel.text((W - len(msg)*4)//2, H//2, msg, 7)

        pyxel.text(5, H-10, "TAB to return", 5)

        esc_text = "ESC to exit"
        pyxel.text(W - len(esc_text)*4 - 5, H-10, esc_text, 5)


App()

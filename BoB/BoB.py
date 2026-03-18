import pyxel
import settings

W, H = 320, 240

class App:
    def __init__(self):
        pyxel.init(W, H, title="Brains Over Bytes")

        self.state = "menu"
        self.menu_items = ["START GAME", "DIFFICULTY", "OPTIONS", "CREDITS"]
        self.selected = 0

        self.diff_items = ["EASY", "MEDIUM", "HARD"]
        self.diff_selected = 0

        pyxel.run(self.update, self.draw)

    # ───────── UPDATE ─────────
    def update(self):
        if self.state == "menu":
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.selected = (self.selected + 1) % len(self.menu_items)
            if pyxel.btnp(pyxel.KEY_UP):
                self.selected = (self.selected - 1) % len(self.menu_items)
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.select_menu()

        elif self.state == "difficulty":
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.diff_selected = (self.diff_selected + 1) % 3
            if pyxel.btnp(pyxel.KEY_UP):
                self.diff_selected = (self.diff_selected - 1) % 3
            if pyxel.btnp(pyxel.KEY_RETURN):
                settings.difficulty = self.diff_items[self.diff_selected]
                self.state = "menu"
            if pyxel.btnp(pyxel.KEY_BACKSPACE):
                self.state = "menu"

        elif self.state == "game":
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                self.state = "menu"

    def select_menu(self):
        choice = self.menu_items[self.selected]
        if choice == "START GAME":
            self.state = "game"
        elif choice == "DIFFICULTY":
            self.state = "difficulty"

    # ───────── DRAW ─────────
    def draw(self):
        pyxel.cls(0)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "difficulty":
            self.draw_menu()
            self.draw_difficulty()
        elif self.state == "game":
            self.draw_game()

    # 🎮 MENU
    def draw_menu(self):
        for y in range(H):
            col = 1 if y < H//2 else 0
            pyxel.line(0, y, W, y, col)

        # 🔥 TITLE
        title = "BRAINS OVER BYTES"
        scale = 3

        total_w = len(title) * (3 * scale + scale)
        start_x = (W - total_w) // 2
        y = 30

        self.draw_block_text(start_x, y, title, scale, 8)

        # 🎯 CENTERED INSERT COIN
        if pyxel.frame_count % 40 < 20:
            text = "INSERT COIN"
            text_w = len(text) * 4
            pyxel.text((W - text_w)//2, 80, text, 11)

        # menu box
        pyxel.rect(90, 110, 140, 90, 0)
        pyxel.rectb(90, 110, 140, 90, 8)

        for i, item in enumerate(self.menu_items):
            y = 130 + i * 18
            color = 7

            if i == self.selected:
                color = 10
                pyxel.text(100, y, "▶", 10)

            pyxel.text(120, y, item, color)

    # 🧱 BLOCK TEXT
    def draw_block_text(self, x, y, text, scale, col):
        for i, ch in enumerate(text):
            cx = x + i * (3 * scale + scale)
            self.draw_block_char(cx, y, ch, scale, col)

    def draw_block_char(self, x, y, ch, s, col):
        patterns = {
            "A": ["010","101","111","101","101","000","000","000"],
            "B": ["110","101","110","101","110","000","000","000"],
            "R": ["110","101","110","101","101","000","000","000"],
            "I": ["111","010","010","010","111","000","000","000"],
            "N": ["101","111","111","111","101","000","000","000"],
            "S": ["111","100","111","001","111","000","000","000"],
            "O": ["111","101","101","101","111","000","000","000"],
            "V": ["101","101","101","101","010","000","000","000"],
            "E": ["111","100","110","100","111","000","000","000"],
            "Y": ["101","101","010","010","010","000","000","000"],
            "T": ["111","010","010","010","010","000","000","000"],
            " ": ["000"] * 8
        }

        pattern = patterns.get(ch, patterns[" "])

        for row, line in enumerate(pattern):
            for col_i, bit in enumerate(line):
                if bit == "1":
                    pyxel.rect(
                        x + col_i * s,
                        y + row * s,
                        s,
                        s,
                        col
                    )

    # ⚙️ DIFFICULTY MENU
    def draw_difficulty(self):
        pyxel.rect(70, 70, 180, 100, 0)
        pyxel.rectb(70, 70, 180, 100, 11)

        self.glow_text(100, 80, "SELECT DIFFICULTY", 10)

        for i, d in enumerate(self.diff_items):
            y = 105 + i * 20
            color = 7

            if i == self.diff_selected:
                color = 10
                pyxel.text(90, y, "▶", 10)

            pyxel.text(120, y, d, color)

    # 🌆 GAME
    def draw_game(self):
        pyxel.cls(0)

        # sky
        for y in range(0, 120):
            if y < 40:
                col = 1
            elif y < 80:
                col = 2
            else:
                col = 3
            pyxel.line(0, y, W, y, col)

        # skyline
        skyline = [40, 50, 45, 60, 35, 55, 42, 48, 38, 52]
        for i, h in enumerate(skyline):
            pyxel.rect(i*32, 120-h, 28, h, 0)

        pyxel.rect(0, 120, W, 5, 1)

        # road
        for i in range(100):
            pyxel.line(160 - i*2, 240, 160 - i, 140, 8)
            pyxel.line(160 + i*2, 240, 160 + i, 140, 8)

        pyxel.line(160, 240, 160, 140, 7)

        # diner
        diner_x = 20
        diner_y = 90
        diner_w = 90
        diner_h = 80

        pyxel.rect(diner_x, diner_y, diner_w, diner_h, 5)

        if settings.difficulty == "EASY":
            win_col = 11
        elif settings.difficulty == "MEDIUM":
            win_col = 10
        else:
            win_col = 8

        for i in range(3):
            x = diner_x + 10 + i*25
            y = diner_y + 20
            pyxel.rect(x, y, 18, 30, win_col)
            pyxel.rectb(x-1, y-1, 20, 32, win_col)

        for i in range(4):
            pyxel.rect(diner_x-i, diner_y-5-i, diner_w+i*2, 5+i, 8)

        # sign
        sign_w = 60
        sign_h = 20
        sign_x = diner_x + diner_w//2 - sign_w//2
        sign_y = diner_y - 25

        pyxel.rect(sign_x, sign_y, sign_w, sign_h, 2)
        pyxel.rectb(sign_x, sign_y, sign_w, sign_h, 14)

        text = "DINER"
        text_w = len(text) * 4
        text_x = sign_x + (sign_w - text_w) // 2
        text_y = sign_y + (sign_h - 6) // 2

        pyxel.text(text_x, text_y, text, 7)

        # car
        self.draw_car(190, 150)

        # street light
        pyxel.rect(250, 80, 3, 100, 1)
        for r in range(1, 6):
            pyxel.circ(251, 80, r, 10)
        pyxel.circ(251, 80, 2, 7)

        pyxel.text(5, 5, f"DIFF: {settings.difficulty}", 7)

    # 🚗 CAR
    def draw_car(self, x, y):
        pyxel.rect(x, y, 40, 10, 2)
        pyxel.rect(x+10, y-8, 20, 8, 2)
        pyxel.rect(x+12, y-6, 6, 4, 7)
        pyxel.circ(x+8, y+10, 3, 0)
        pyxel.circ(x+30, y+10, 3, 0)
        pyxel.rect(x+40, y+2, 4, 3, 7)

        for i in range(20):
            pyxel.line(x+44, y+3, x+60+i, y-5+i//2, 10)

    def glow_text(self, x, y, txt, col):
        pyxel.text(x-1, y, txt, col)
        pyxel.text(x+1, y, txt, col)
        pyxel.text(x, y-1, txt, col)
        pyxel.text(x, y+1, txt, col)
        pyxel.text(x, y, txt, 7)


App()
import pyxel

# SCREEN SIZE
W, H = 320, 240


class App:
    def __init__(self):
        pyxel.init(W, H, title="Brains Over Bytes")

        self.state = "menu"

        # 🎮 GAME LIST (5 games)
        self.games = [
            "Game 1",
            "Game 2",
            "Game 3",
            "Game 4",
            "Game 5"
        ]
        self.selected = 0

        pyxel.run(self.update, self.draw)

    # ───────── UPDATE ─────────
    def update(self):
        if self.state == "menu":
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.selected = (self.selected + 1) % len(self.games)

            if pyxel.btnp(pyxel.KEY_UP):
                self.selected = (self.selected - 1) % len(self.games)

            if pyxel.btnp(pyxel.KEY_RETURN):
                game_name = self.games[self.selected]
                self.state = f"game_{self.selected+1}"  # Use index for easier routing

        elif self.state.startswith("game_"):
            # TAB → return to menu
            if pyxel.btnp(pyxel.KEY_TAB):
                self.state = "menu"

            # ESC → quit game
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                pyxel.quit()

    # ───────── DRAW ─────────
    def draw(self):
        pyxel.cls(0)

        if self.state == "menu":
            self.draw_menu()

        elif self.state.startswith("game_"):
            self.draw_game_screen()

    # 🎮 MAIN ARCADE MENU
    def draw_menu(self):
        # background split
        for y in range(H):
            col = 1 if y < H // 2 else 0
            pyxel.line(0, y, W, y, col)

        # 🔴 BIG TITLE
        title = "ARCADE HUB"
        scale = 4
        total_width = len(title) * (4 * scale)
        start_x = (W - total_width) // 2

        # glow effect
        self.draw_big_text(start_x-1, 20, title, scale, 2)
        self.draw_big_text(start_x+1, 20, title, scale, 2)
        self.draw_big_text(start_x, 19, title, scale, 2)
        self.draw_big_text(start_x, 21, title, scale, 2)

        # main red text
        self.draw_big_text(start_x, 20, title, scale, 8)

        # INSERT COIN BLINK
        if pyxel.frame_count % 40 < 20:
            text = "INSERT COIN"
            pyxel.text((W - len(text) * 4) // 2, 70, text, 10)

        # MENU BOX (shifted down 2 pixels)
        pyxel.rect(80, 102, 160, 110, 0)
        pyxel.rectb(80, 102, 160, 110, 7)

        # GAME LIST
        for i, game in enumerate(self.games):
            y = 122 + i * 14  # slightly down inside box

            # 🪙 QUARTER CURSOR
            if i == self.selected:
                pyxel.circ(95, y + 3, 2, 10)

            pyxel.text(110, y, game, 7)

    # 🕹️ PLACEHOLDER GAME SCREEN
    def draw_game_screen(self):
        pyxel.cls(0)

        game_index = int(self.state.split("_")[1])
        game_name = f"Game {game_index}"

        msg = f"INSERT {game_name} HERE"
        pyxel.text((W - len(msg) * 4) // 2, H // 2, msg, 7)

        # Bottom-left → TAB
        pyxel.text(5, H - 10, "TAB to return", 5)

        # Bottom-right → ESC
        esc_text = "ESC to exit"
        pyxel.text(W - len(esc_text)*4 - 5, H - 10, esc_text, 5)

    # 🔴 BIG PIXEL TEXT FUNCTION
    def draw_big_text(self, x, y, text, scale, col):
        patterns = {
            "A": ["010","101","111","101","101"],
            "B": ["110","101","110","101","110"],
            "C": ["111","100","100","100","111"],
            "D": ["110","101","101","101","110"],
            "E": ["111","100","110","100","111"],
            "H": ["101","101","111","101","101"],
            "I": ["111","010","010","010","111"],
            "O": ["111","101","101","101","111"],
            "R": ["110","101","110","101","101"],
            "U": ["101","101","101","101","111"],
            " ": ["000","000","000","000","000"]
        }

        for i, ch in enumerate(text):
            pattern = patterns.get(ch, patterns[" "])
            for row, line in enumerate(pattern):
                for col_i, bit in enumerate(line):
                    if bit == "1":
                        pyxel.rect(
                            x + i * (4 * scale) + col_i * scale,
                            y + row * scale,
                            scale,
                            scale,
                            col
                        )


# RUN THE APP
App()

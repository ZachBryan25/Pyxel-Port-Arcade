import pyxel
from Space_Invaders import Game as SpaceInvadersGame

# SCREEN SIZE
W, H = 320, 240


class App:
    def __init__(self):
        pyxel.init(W, H, title="Pyxel Port")

        self.state = "menu"
        self.current_game = None

        # 🎮 GAME LIST (TEAMMATES EDIT THESE)
        self.games = [
            "Space Invaders",
            "Game 2",
            "Game 3",
            "Game 4",
            "Game 5"
        ]

        self.selected = 0

        pyxel.run(self.update, self.draw)

    def launch_selected_game(self):
        if self.selected == 0:
            self.current_game = SpaceInvadersGame(return_to_menu=self.return_to_menu)
            self.state = "game_1"
        else:
            self.state = f"game_{self.selected+1}"

    def return_to_menu(self):
        self.current_game = None
        self.state = "menu"

    # ───────── UPDATE ─────────
    def update(self):

        # 🎮 MAIN MENU
        if self.state == "menu":
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.selected = (self.selected + 1) % len(self.games)

            if pyxel.btnp(pyxel.KEY_UP):
                self.selected = (self.selected - 1) % len(self.games)

            if pyxel.btnp(pyxel.KEY_RETURN):
                self.launch_selected_game()

        # 🎮 SPACE INVADERS (Game 1)
        elif self.state == "game_1":
            if self.current_game is not None:
                self.current_game.update()

        # 🎮 PLACEHOLDER GAME STATES
        elif self.state.startswith("game_") and self.state != "game_1":

            # TAB → return to menu
            if pyxel.btnp(pyxel.KEY_TAB):
                self.state = "menu"

            # ESC → quit program (ONLY for placeholder games)
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                pyxel.quit()

    # ───────── DRAW ─────────
    def draw(self):
        pyxel.cls(0)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "game_1":
            if self.current_game is not None:
                self.current_game.draw()
        else:
            self.draw_placeholder()

    # 🎮 MAIN MENU
    def draw_menu(self):

        # Background split
        for y in range(H):
            pyxel.line(0, y, W, y, 1 if y < H // 2 else 0)

        # 🔴 BIG TITLE
        title = "PYXEL PORT"
        scale = 4
        start_x = (W - len(title) * (3 * scale + scale)) // 2
        y = 40

        for i, ch in enumerate(title):
            self.draw_block_char(start_x + i * (3 * scale + scale), y, ch, scale, 8)

        # 💰 INSERT COIN
        if pyxel.frame_count % 40 < 20:
            text = "INSERT COIN"
            pyxel.text((W - len(text) * 4) // 2, 95, text, 10)

        # 📦 MENU BOX
        pyxel.rect(80, 102, 160, 110, 0)
        pyxel.rectb(80, 102, 160, 110, 7)

        # 🎯 GAME LIST
        for i, game in enumerate(self.games):
            y = 122 + i * 14

            if i == self.selected:
                pyxel.circ(95, y + 3, 2, 10)

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
                    pyxel.rect(x + col_i * s, y + row * s, s, s, col)

    # 🕹️ PLACEHOLDER SCREEN
    def draw_placeholder(self):
        pyxel.cls(0)

        game_index = int(self.state.split("_")[1])
        game_name = self.games[game_index - 1]

        msg = f"INSERT {game_name} HERE"
        pyxel.text((W - len(msg) * 4) // 2, H // 2, msg, 7)

        pyxel.text(5, H - 10, "TAB to return", 5)

        esc_text = "ESC to exit"
        pyxel.text(W - len(esc_text) * 4 - 5, H - 10, esc_text, 5)


App()
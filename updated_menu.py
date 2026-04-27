import os
import sys
import pyxel

W, H = 320, 240


class App:
    def __init__(self):
        pyxel.init(W, H, title="Pyxel Port")

        self.games = [
            ("Space Invaders", "Space_Invaders.py"),
            ("Dungeon Shooter", "dungeon_shooter.py"),
            ("Pong", "pong.py"),
            ("Solitaire", "solitaire.py"),
            ("Random Access Match", "R_A_M.py"),
        ]

        self.selected = 0
        pyxel.run(self.update, self.draw)

    def launch_selected_game(self):
        game_name, file_name = self.games[self.selected]

        if not os.path.exists(file_name):
            print(f"ERROR: Could not find {file_name}")
            print("Make sure all .py game files are in the same folder as this menu file.")
            return

        os.execv(sys.executable, [sys.executable, file_name])

    def update(self):
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.selected = (self.selected + 1) % len(self.games)

        if pyxel.btnp(pyxel.KEY_UP):
            self.selected = (self.selected - 1) % len(self.games)

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.launch_selected_game()

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

    def draw(self):
        self.draw_menu()

    def draw_menu(self):
        pyxel.cls(0)

        pyxel.rect(0, 0, W, 145, 1)
        pyxel.rect(0, 145, W, 95, 0)

        for x in range(20, W, 28):
            h = 30 + (x % 50)
            pyxel.rect(x, 80 - h // 2, 12, h, 5)
            pyxel.rectb(x, 80 - h // 2, 12, h, 13)
            for yy in range(84 - h // 2, 78 + h // 2, 8):
                pyxel.pset(x + 3, yy, 10)
                pyxel.pset(x + 8, yy + 2, 12)

        for y in range(150, H, 12):
            pyxel.line(0, y, W, y, 5)
        for x in range(-80, W + 80, 24):
            pyxel.line(W // 2, 145, x, H, 13)

        pyxel.rect(8, 65, 55, 115, 0)
        pyxel.rectb(8, 65, 55, 115, 5)
        pyxel.rect(14, 72, 43, 13, 8)
        pyxel.text(22, 76, "ARCADE", 10)
        pyxel.rect(17, 92, 35, 34, 1)
        pyxel.rectb(17, 92, 35, 34, 12)
        pyxel.text(22, 104, "PLAY", 7)
        pyxel.rect(15, 133, 40, 18, 5)
        pyxel.circ(25, 141, 3, 8)
        pyxel.circ(38, 141, 2, 10)
        pyxel.circ(46, 141, 2, 12)

        pyxel.rect(258, 60, 54, 120, 0)
        pyxel.rectb(258, 60, 54, 120, 13)
        pyxel.rect(264, 67, 42, 13, 2)
        pyxel.text(270, 71, "SPACE", 10)
        pyxel.rect(267, 88, 34, 36, 1)
        pyxel.rectb(267, 88, 34, 36, 12)
        pyxel.text(274, 101, "ALIEN", 11)
        pyxel.rect(265, 132, 40, 18, 5)
        pyxel.circ(276, 140, 3, 8)
        pyxel.circ(290, 140, 2, 10)
        pyxel.circ(298, 140, 2, 12)

        pyxel.rect(235, 18, 68, 30, 0)
        pyxel.rectb(235, 18, 68, 30, 13)
        pyxel.text(247, 28, "INSERT", 8)
        pyxel.text(255, 38, "COIN", 10)

        pyxel.circ(160, 18, 18, 2)
        pyxel.circb(160, 18, 24, 8)
        pyxel.rect(145, 15, 30, 5, 8)

        title = "PYXEL PORT"
        scale = 4
        start_x = (W - len(title) * (3 * scale + scale)) // 2
        y = 38

        for i, ch in enumerate(title):
            self.draw_block_char(start_x + i * (3 * scale + scale), y, ch, scale, 8)

        if pyxel.frame_count % 40 < 20:
            text = "INSERT COIN"
            pyxel.text((W - len(text) * 4) // 2, 91, text, 10)

        pyxel.rect(70, 102, 180, 110, 0)
        pyxel.rectb(70, 102, 180, 110, 7)
        pyxel.rectb(72, 104, 176, 106, 5)

        for i, (game_name, file_name) in enumerate(self.games):
            y = 122 + i * 14

            if i == self.selected:
                pyxel.circ(85, y + 3, 3, 10)
                pyxel.text(100, y, game_name, 10)
            else:
                pyxel.text(100, y, game_name, 7)

        pyxel.text(70, 225, "UP/DOWN = MOVE   ENTER = PLAY   ESC = QUIT", 6)

    def draw_block_char(self, x, y, ch, s, col):
        patterns = {
            "P": ["110", "101", "110", "100", "100"],
            "Y": ["101", "101", "010", "010", "010"],
            "X": ["101", "010", "010", "010", "101"],
            "E": ["111", "100", "110", "100", "111"],
            "L": ["100", "100", "100", "100", "111"],
            "O": ["111", "101", "101", "101", "111"],
            "R": ["110", "101", "110", "101", "101"],
            "T": ["111", "010", "010", "010", "010"],
            " ": ["000", "000", "000", "000", "000"],
        }

        pattern = patterns.get(ch, patterns[" "])

        for row, line in enumerate(pattern):
            for col_i, bit in enumerate(line):
                if bit == "1":
                    pyxel.rect(x + col_i * s, y + row * s, s, s, col)


App()

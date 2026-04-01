import pyxel

WIDTH = 160
HEIGHT = 120

class Pong:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Pong")

        self.state = "menu"
        self.reset()

        pyxel.run(self.update, self.draw)

    def reset(self):
        self.paddle_y = HEIGHT // 2 - 10
        self.enemy_y = HEIGHT // 2 - 10
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_vx = 2
        self.ball_vy = 2
        self.player_score = 0
        self.enemy_score = 0

    def update(self):
        if self.state == "menu":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.state = "play"
            return

        if self.state == "gameover":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset()
                self.state = "menu"
            return

        if pyxel.btn(pyxel.KEY_UP):
            self.paddle_y -= 3
        if pyxel.btn(pyxel.KEY_DOWN):
            self.paddle_y += 3

        self.paddle_y = max(0, min(HEIGHT - 20, self.paddle_y))

        if self.ball_y > self.enemy_y:
            self.enemy_y += 2
        elif self.ball_y < self.enemy_y:
            self.enemy_y -= 2

        self.enemy_y = max(0, min(HEIGHT - 20, self.enemy_y))

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        if self.ball_y <= 0 or self.ball_y >= HEIGHT:
            self.ball_vy *= -1

        if self.ball_x <= 10 and self.paddle_y <= self.ball_y <= self.paddle_y + 20:
            self.ball_vx *= -1

        if self.ball_x >= WIDTH - 10 and self.enemy_y <= self.ball_y <= self.enemy_y + 20:
            self.ball_vx *= -1

        if self.ball_x < 0:
            self.enemy_score += 1
            self.ball_x, self.ball_y = WIDTH // 2, HEIGHT // 2

        if self.ball_x > WIDTH:
            self.player_score += 1
            self.ball_x, self.ball_y = WIDTH // 2, HEIGHT // 2

        if self.player_score >= 5 or self.enemy_score >= 5:
            self.state = "gameover"

    def draw(self):
        pyxel.cls(0)

        if self.state == "menu":
            pyxel.text(WIDTH//2 - 20, HEIGHT//2 - 10, "PONG", 7)
            pyxel.text(WIDTH//2 - 40, HEIGHT//2 + 10, "Press ENTER to Start", 7)
            return

        if self.state == "gameover":
            winner = "You Win!" if self.player_score > self.enemy_score else "You Lose!"
            pyxel.text(WIDTH//2 - 30, HEIGHT//2 - 10, winner, 7)
            pyxel.text(WIDTH//2 - 40, HEIGHT//2 + 10, "Press ENTER for Menu", 7)
            return

        pyxel.rect(5, self.paddle_y, 3, 20, 7)
        pyxel.rect(WIDTH - 8, self.enemy_y, 3, 20, 7)

        pyxel.circ(self.ball_x, self.ball_y, 2, 7)

        pyxel.text(10, 5, f"{self.player_score}", 7)
        pyxel.text(WIDTH - 20, 5, f"{self.enemy_score}", 7)


Pong()

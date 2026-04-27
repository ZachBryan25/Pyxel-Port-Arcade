import pyxel

WIDTH = 160
HEIGHT = 120

PADDLE_HEIGHT = 20
BALL_START_SPEED = 2
WINNING_SCORE = 5

PLAYER_SPEED = 3
HIT_SPEED_INCREASE = 1.08
MAX_SPEED = 6


class Pong:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Tennis Pong")
        self.state = "menu"
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.paddle_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.enemy_y = HEIGHT // 2 - PADDLE_HEIGHT // 2

        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_vx = BALL_START_SPEED
        self.ball_vy = BALL_START_SPEED

        self.player_score = 0
        self.enemy_score = 0

    def reset_ball(self, direction):
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_vx = BALL_START_SPEED * direction
        self.ball_vy = BALL_START_SPEED

    def increase_ball_speed(self):
        # increase speed but cap it
        self.ball_vx = max(min(self.ball_vx * HIT_SPEED_INCREASE, MAX_SPEED), -MAX_SPEED)
        self.ball_vy = max(min(self.ball_vy * HIT_SPEED_INCREASE, MAX_SPEED), -MAX_SPEED)

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

        self.update_player()
        self.update_enemy()
        self.update_ball()
        self.check_score()
        self.check_gameover()

    def update_player(self):
        if pyxel.btn(pyxel.KEY_UP):
            self.paddle_y -= PLAYER_SPEED
        if pyxel.btn(pyxel.KEY_DOWN):
            self.paddle_y += PLAYER_SPEED

        self.paddle_y = max(0, min(HEIGHT - PADDLE_HEIGHT, self.paddle_y))

    def update_enemy(self):
        # strong but not perfect AI
        enemy_speed = 3.2

        if pyxel.frame_count % 5 == 0:
            return  # slight delay

        target_y = self.ball_y - PADDLE_HEIGHT // 2

        # occasional mistake
        if pyxel.frame_count % 90 < 15:
            target_y += 6

        if target_y > self.enemy_y:
            self.enemy_y += enemy_speed
        elif target_y < self.enemy_y:
            self.enemy_y -= enemy_speed

        self.enemy_y = max(0, min(HEIGHT - PADDLE_HEIGHT, self.enemy_y))

    def update_ball(self):
        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

        if self.ball_y <= 0 or self.ball_y >= HEIGHT:
            self.ball_vy *= -1

        # player hit
        if self.ball_x <= 10 and self.paddle_y <= self.ball_y <= self.paddle_y + PADDLE_HEIGHT:
            self.ball_vx = abs(self.ball_vx)
            self.increase_ball_speed()

        # enemy hit
        if self.ball_x >= WIDTH - 10 and self.enemy_y <= self.ball_y <= self.enemy_y + PADDLE_HEIGHT:
            self.ball_vx = -abs(self.ball_vx)
            self.increase_ball_speed()

    def check_score(self):
        if self.ball_x < 0:
            self.enemy_score += 1
            self.reset_ball(direction=-1)

        if self.ball_x > WIDTH:
            self.player_score += 1
            self.reset_ball(direction=1)

    def check_gameover(self):
        if self.player_score >= WINNING_SCORE or self.enemy_score >= WINNING_SCORE:
            self.state = "gameover"

    def draw(self):
        if self.state == "menu":
            self.draw_tennis_court()
            self.draw_menu()
            return

        if self.state == "gameover":
            self.draw_tennis_court()
            self.draw_gameover()
            return

        self.draw_game()

    def draw_tennis_court(self):
        # DARK GREEN background (replaces purple)
        pyxel.cls(3)

        court_x = 8
        court_y = 8
        court_w = WIDTH - 16
        court_h = HEIGHT - 16

        # inner court (light blue)
        pyxel.rect(court_x, court_y, court_w, court_h, 12)

        # horizontal lines
        pyxel.line(court_x, court_y + 18, court_x + court_w, court_y + 18, 7)
        pyxel.line(court_x, court_y + court_h - 18, court_x + court_w, court_y + court_h - 18, 7)

        # vertical lines
        pyxel.line(court_x + 10, court_y, court_x + 10, court_y + court_h, 7)
        pyxel.line(court_x + court_w - 10, court_y, court_x + court_w - 10, court_y + court_h, 7)

        # center lines
        pyxel.line(WIDTH // 2, court_y, WIDTH // 2, court_y + court_h, 7)
        pyxel.line(court_x, HEIGHT // 2, court_x + court_w, HEIGHT // 2, 7)

    def draw_menu(self):
        pyxel.rect(35, 42, 90, 35, 0)
        pyxel.rectb(35, 42, 90, 35, 7)
        pyxel.text(WIDTH // 2 - 24, HEIGHT // 2 - 14, "TENNIS PONG", 10)
        pyxel.text(WIDTH // 2 - 42, HEIGHT // 2 + 4, "Press ENTER to Start", 7)

    def draw_gameover(self):
        winner = "You Win!" if self.player_score > self.enemy_score else "You Lose!"

        pyxel.rect(35, 42, 90, 35, 0)
        pyxel.rectb(35, 42, 90, 35, 7)
        pyxel.text(WIDTH // 2 - 30, HEIGHT // 2 - 10, winner, 10)
        pyxel.text(WIDTH // 2 - 40, HEIGHT // 2 + 8, "Press ENTER for Menu", 7)

    def draw_game(self):
        self.draw_tennis_court()

        # player paddle (green)
        pyxel.rect(5, self.paddle_y, 3, PADDLE_HEIGHT, 11)

        # enemy paddle (red)
        pyxel.rect(WIDTH - 8, self.enemy_y, 3, PADDLE_HEIGHT, 8)

        # ball (light yellow)
        pyxel.circ(self.ball_x, self.ball_y, 2, 10)

        pyxel.text(10, 2, str(self.player_score), 7)
        pyxel.text(WIDTH - 20, 2, str(self.enemy_score), 7)


Pong()

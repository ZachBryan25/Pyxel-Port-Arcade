import random
import pyxel


SCREEN_W = 320
SCREEN_H = 240
PLAYER_Y = 214
STAR_COUNT = 70
MAX_LEVEL = 15


class Bullet:
    def __init__(self, x, y, dy, friendly=True):
        self.x = x
        self.y = y
        self.dy = dy
        self.friendly = friendly
        self.w = 3
        self.h = 6
        self.alive = True

    def update(self):
        self.y += self.dy
        if self.y < -8 or self.y > SCREEN_H + 8:
            self.alive = False

    def draw(self):
        color = 10 if self.friendly else 8
        pyxel.rect(int(self.x), int(self.y), self.w, self.h, color)


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 14

    def update(self):
        self.timer -= 1

    def draw(self):
        radius = max(1, 14 - self.timer)
        color = 10 if self.timer % 2 == 0 else 7
        pyxel.circb(int(self.x), int(self.y), radius, color)
        if radius > 2:
            pyxel.circb(int(self.x), int(self.y), radius - 2, 8)

    @property
    def alive(self):
        return self.timer > 0


class Enemy:
    def __init__(self, x, y, row, level):
        self.x = x
        self.y = y
        self.row = row
        self.w = 16
        self.h = 12
        self.alive = True
        self.anim = random.randint(0, 20)
        self.hp = 1 + (1 if level >= 8 and row == 0 else 0) + (1 if level >= 13 and row <= 1 else 0)

    def hit(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, frame_count):
        phase = (frame_count // 12 + self.anim) % 2
        base = 11 if self.row == 0 else 9 if self.row in (1, 2) else 8
        color = 7 if self.hp >= 3 else 10 if self.hp == 2 else base
        x = int(self.x)
        y = int(self.y)

        if phase == 0:
            pyxel.rect(x + 3, y, 10, 3, color)
            pyxel.rect(x + 1, y + 3, 14, 3, color)
            pyxel.rect(x + 3, y + 6, 10, 3, color)
            pyxel.pset(x + 3, y + 10, color)
            pyxel.pset(x + 12, y + 10, color)
            pyxel.pset(x + 2, y + 9, color)
            pyxel.pset(x + 13, y + 9, color)
        else:
            pyxel.rect(x + 3, y, 10, 3, color)
            pyxel.rect(x + 1, y + 3, 14, 3, color)
            pyxel.rect(x + 3, y + 6, 10, 3, color)
            pyxel.pset(x + 1, y + 10, color)
            pyxel.pset(x + 14, y + 10, color)
            pyxel.pset(x + 4, y + 9, color)
            pyxel.pset(x + 11, y + 9, color)


class Shield:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 30
        self.h = 16
        self.hp = 24

    @property
    def alive(self):
        return self.hp > 0

    def damage(self, amount=1):
        self.hp = max(0, self.hp - amount)

    def draw(self):
        if not self.alive:
            return
        color = 11 if self.hp > 14 else 10 if self.hp > 7 else 8
        x = int(self.x)
        y = int(self.y)
        pyxel.rect(x, y, self.w, 9, color)
        pyxel.rect(x + 3, y + 9, 6, 7, color)
        pyxel.rect(x + 21, y + 9, 6, 7, color)
        notch_w = max(4, 12 - (24 - self.hp) // 2)
        pyxel.rect(x + 15 - notch_w // 2, y + 9, notch_w, 7, 0)


class Player:
    def __init__(self):
        self.w = 18
        self.h = 10
        self.reset()

    def reset(self):
        self.x = SCREEN_W // 2 - self.w // 2
        self.y = PLAYER_Y
        self.cooldown = 0
        self.respawn_timer = 0
        self.invuln_timer = 90

    @property
    def active(self):
        return self.respawn_timer == 0

    def hit(self):
        if self.invuln_timer > 0 or self.respawn_timer > 0:
            return False
        self.respawn_timer = 45
        self.cooldown = 0
        return True

    def update(self, move_speed):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.invuln_timer > 0:
            self.invuln_timer -= 1

        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                self.x = SCREEN_W // 2 - self.w // 2
                self.invuln_timer = 90
            return

        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.x -= move_speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.x += move_speed

        self.x = max(8, min(SCREEN_W - self.w - 8, self.x))

    def can_fire(self):
        return self.respawn_timer == 0 and self.cooldown == 0

    def fire(self):
        self.cooldown = 10
        return Bullet(self.x + self.w // 2 - 1, self.y - 4, -5, True)

    def draw(self, frame_count):
        if self.respawn_timer > 0 and frame_count % 6 < 3:
            return

        color = 6 if self.invuln_timer > 0 and frame_count % 8 < 4 else 7
        x = int(self.x)
        y = int(self.y)
        pyxel.rect(x + 6, y, 6, 3, color)
        pyxel.rect(x + 3, y + 3, 12, 3, color)
        pyxel.rect(x, y + 6, 18, 3, color)
        pyxel.rect(x + 8, y - 3, 2, 3, color)


class Game:
    def __init__(self, return_to_menu=None):
        self.return_to_menu = return_to_menu
        self.stars = [
            (random.randint(0, SCREEN_W - 1), random.randint(0, SCREEN_H - 1), random.choice([1, 5, 13]))
            for _ in range(STAR_COUNT)
        ]
        self.reset_run()

    def reset_run(self):
        self.player = Player()
        self.level = 1
        self.score = 0
        self.lives = 3
        self.level_cleared_timer = 0
        self.game_over = False
        self.victory = False
        self.explosions = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.shields = []
        self.message_timer = 90
        self.load_level(self.level)

    def level_config(self, level):
        rows = min(5, 3 + (level - 1) // 3)
        cols = min(10, 5 + (level - 1) // 2)
        enemy_speed = 0.30 + level * 0.07
        drop_distance = 5 + level // 4
        fire_rate = min(0.004 + level * 0.0018, 0.05)
        shield_count = 4 if level <= 5 else 3 if level <= 10 else 2
        player_speed = 2.3 + min(level * 0.05, 1.0)
        kills_to_advance = rows * cols
        return {
            "rows": rows,
            "cols": cols,
            "enemy_speed": enemy_speed,
            "drop_distance": drop_distance,
            "fire_rate": fire_rate,
            "shield_count": shield_count,
            "player_speed": player_speed,
            "kills_to_advance": kills_to_advance,
        }

    def load_level(self, level):
        self.config = self.level_config(level)
        self.enemies = []
        start_x = 36
        start_y = 34
        spacing_x = 24
        spacing_y = 18

        for row in range(self.config["rows"]):
            for col in range(self.config["cols"]):
                self.enemies.append(Enemy(start_x + col * spacing_x, start_y + row * spacing_y, row, level))

        self.enemy_dir = 1
        self.enemy_move_accumulator = 0.0
        self.level_kills = 0
        self.player_bullets = []
        self.enemy_bullets = []
        self.player.x = SCREEN_W // 2 - self.player.w // 2
        self.player.cooldown = 0
        self.player.respawn_timer = 0
        self.player.invuln_timer = max(self.player.invuln_timer, 45)
        self.shields = []

        if self.config["shield_count"] > 0:
            spacing = SCREEN_W // (self.config["shield_count"] + 1)
            for i in range(self.config["shield_count"]):
                self.shields.append(Shield(spacing * (i + 1) - 15, 172))

        self.message_timer = 70

    def rects_overlap(self, ax, ay, aw, ah, bx, by, bw, bh):
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

    def update_stars(self):
        updated = []
        for x, y, color in self.stars:
            y += 0.15 + color * 0.01
            if y >= SCREEN_H:
                y = 0
                x = random.randint(0, SCREEN_W - 1)
            updated.append((x, y, color))
        self.stars = updated

    def update(self):
        self.update_stars()

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            if self.return_to_menu is not None:
                self.return_to_menu()
            return

        if self.game_over or self.victory:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_run()
            return

        if self.level_cleared_timer > 0:
            self.level_cleared_timer -= 1
            if self.level_cleared_timer == 0:
                self.level += 1
                if self.level > MAX_LEVEL:
                    self.victory = True
                else:
                    self.load_level(self.level)
            return

        if self.message_timer > 0:
            self.message_timer -= 1

        self.player.update(self.config["player_speed"])

        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)) and self.player.can_fire():
            self.player_bullets.append(self.player.fire())

        self.update_enemy_swarm()
        self.update_bullets()
        self.update_explosions()
        self.check_level_progress()
        self.check_enemy_reach_bottom()

    def update_enemy_swarm(self):
        living = [enemy for enemy in self.enemies if enemy.alive]
        if not living:
            return

        speed_boost = 1 + (self.level_kills / max(1, self.config["kills_to_advance"])) * 1.5
        self.enemy_move_accumulator += self.config["enemy_speed"] * speed_boost

        while self.enemy_move_accumulator >= 1:
            self.enemy_move_accumulator -= 1
            step = self.enemy_dir
            hit_edge = False

            for enemy in living:
                next_x = enemy.x + step
                if next_x < 8 or next_x + enemy.w > SCREEN_W - 8:
                    hit_edge = True
                    break

            if hit_edge:
                self.enemy_dir *= -1
                for enemy in living:
                    enemy.y += self.config["drop_distance"]
            else:
                for enemy in living:
                    enemy.x += step

        columns = {}
        for enemy in living:
            key = int((enemy.x + enemy.w / 2) // 8)
            if key not in columns or enemy.y > columns[key].y:
                columns[key] = enemy

        shooters = list(columns.values())
        bullet_cap = 8 + self.level
        available_slots = max(0, bullet_cap - len(self.enemy_bullets))

        if available_slots <= 0:
            return

        random.shuffle(shooters)
        fired = 0
        for shooter in shooters:
            if fired >= available_slots:
                break
            if random.random() < self.config["fire_rate"]:
                speed = 2.1 + min(self.level * 0.14, 2.0)
                self.enemy_bullets.append(Bullet(shooter.x + shooter.w // 2, shooter.y + shooter.h + 1, speed, False))
                fired += 1

    def update_bullets(self):
        for bullet in self.player_bullets:
            bullet.update()
        for bullet in self.enemy_bullets:
            bullet.update()

        for bullet in self.player_bullets:
            if not bullet.alive:
                continue

            for shield in self.shields:
                if shield.alive and self.rects_overlap(bullet.x, bullet.y, bullet.w, bullet.h, shield.x, shield.y, shield.w, shield.h):
                    shield.damage(2)
                    bullet.alive = False
                    self.explosions.append(Explosion(bullet.x, bullet.y))
                    break

            if not bullet.alive:
                continue

            for enemy in self.enemies:
                if enemy.alive and self.rects_overlap(bullet.x, bullet.y, bullet.w, bullet.h, enemy.x, enemy.y, enemy.w, enemy.h):
                    bullet.alive = False
                    destroyed = enemy.hit()
                    self.explosions.append(Explosion(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2))
                    if destroyed:
                        self.level_kills += 1
                        self.score += 10 + (self.level * 3) + (4 - min(enemy.row, 4)) * 2
                    else:
                        self.score += 2
                    break

        for bullet in self.enemy_bullets:
            if not bullet.alive:
                continue

            for shield in self.shields:
                if shield.alive and self.rects_overlap(bullet.x, bullet.y, bullet.w, bullet.h, shield.x, shield.y, shield.w, shield.h):
                    shield.damage(1)
                    bullet.alive = False
                    self.explosions.append(Explosion(bullet.x, bullet.y))
                    break

            if not bullet.alive:
                continue

            if self.player.active and self.rects_overlap(bullet.x, bullet.y, bullet.w, bullet.h, self.player.x, self.player.y - 3, self.player.w, self.player.h + 3):
                bullet.alive = False
                if self.player.hit():
                    self.lives -= 1
                    self.explosions.append(Explosion(self.player.x + self.player.w // 2, self.player.y + 2))
                    if self.lives <= 0:
                        self.game_over = True

        self.player_bullets = [bullet for bullet in self.player_bullets if bullet.alive]
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if bullet.alive]
        self.shields = [shield for shield in self.shields if shield.alive]

    def update_explosions(self):
        for explosion in self.explosions:
            explosion.update()
        self.explosions = [explosion for explosion in self.explosions if explosion.alive]

    def check_level_progress(self):
        remaining = sum(1 for enemy in self.enemies if enemy.alive)
        if remaining == 0:
            self.level_cleared_timer = 75
            self.score += 50 * self.level

    def check_enemy_reach_bottom(self):
        for enemy in self.enemies:
            if enemy.alive and enemy.y + enemy.h >= self.player.y:
                self.game_over = True
                return

    def draw_background(self):
        pyxel.cls(0)
        for x, y, color in self.stars:
            pyxel.pset(int(x), int(y), color)
        pyxel.line(0, SCREEN_H - 20, SCREEN_W, SCREEN_H - 20, 5)

    def draw_hud(self):
        pyxel.text(10, 10, f"SCORE {self.score}", 7)
        pyxel.text(138, 10, f"LEVEL {self.level}", 10)
        pyxel.text(252, 10, f"LIVES {max(0, self.lives)}", 8)

        progress_total = max(1, self.config["kills_to_advance"])
        progress_w = min(96, int(96 * self.level_kills / progress_total))
        pyxel.rectb(112, SCREEN_H - 14, 98, 6, 7)
        pyxel.rect(113, SCREEN_H - 13, progress_w, 4, 11)

    def draw_messages(self):
        if self.message_timer > 0:
            msg = f"LEVEL {self.level}"
            pyxel.rect(132, 100, 56, 16, 1)
            pyxel.rectb(132, 100, 56, 16, 7)
            pyxel.text(147, 105, msg, 7)

        if self.level_cleared_timer > 0:
            pyxel.rect(116, 98, 88, 18, 1)
            pyxel.rectb(116, 98, 88, 18, 10)
            pyxel.text(132, 104, "LEVEL CLEARED", 10)

        if self.game_over:
            pyxel.rect(92, 88, 136, 30, 1)
            pyxel.rectb(92, 88, 136, 30, 8)
            pyxel.text(136, 96, "GAME OVER", 8)
            pyxel.text(102, 106, "R RESTART  ESC MENU", 7)

        if self.victory:
            pyxel.rect(74, 82, 172, 38, 1)
            pyxel.rectb(74, 82, 172, 38, 11)
            pyxel.text(143, 90, "YOU WIN", 11)
            pyxel.text(104, 100, "ALL 15 LEVELS CLEARED", 7)
            pyxel.text(94, 110, "R PLAY AGAIN  ESC MENU", 7)

    def draw(self):
        self.draw_background()
        self.draw_hud()

        for shield in self.shields:
            shield.draw()

        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(pyxel.frame_count)

        for bullet in self.player_bullets:
            bullet.draw()
        for bullet in self.enemy_bullets:
            bullet.draw()

        for explosion in self.explosions:
            explosion.draw()

        self.player.draw(pyxel.frame_count)
        self.draw_messages()
        pyxel.text(10, SCREEN_H - 30, "ARROWS MOVE   SPACE SHOOTS   ESC MENU", 6)


if __name__ == "__main__":
    pyxel.init(SCREEN_W, SCREEN_H, title="Pyxel Space Invaders", fps=60)
    game = Game()
    pyxel.run(game.update, game.draw)

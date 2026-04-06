import pyxel
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Street Crashers - Pyxel fighting game mock (90s arcade vibe)
# Controls:
#   TITLE / MENUS:
#       ENTER: confirm / start
#       ESC: quit
#   CHARACTER SELECT:
#       P1: A/D to move cursor, ENTER to select
#       P2: LEFT/RIGHT to move cursor, ENTER to select
#   STAGE SELECT:
#       A/D or LEFT/RIGHT to choose stage, ENTER to confirm
#   FIGHT:
#       P1: A/D move, W jump, S crouch, J punch, K kick, U special
#       P2: LEFT/RIGHT move, UP jump, DOWN crouch, N punch, M kick, , special
#
# Tip: If you don't have pyxel installed:
#   pip install pyxel

W, H = 256, 144
GROUND_Y = 118

STATE_TITLE = 0
STATE_CHAR_SELECT = 1
STATE_STAGE_SELECT = 2
STATE_FIGHT = 3
STATE_GAME_OVER = 4

STAGES = [
    ("Parking Lot", "Neon diner & cars"),
    ("Rooftop Rumble", "City skyline at night"),
    ("Subway Slam", "Underground platform"),
]


@dataclass
class FighterDef:
    name: str
    # base palette indices used in the 16x16 sprite
    sprite_u: int
    sprite_v: int
    accent_color: int
    special_name: str


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    owner: int
    life: int = 90
    w: int = 6
    h: int = 2


@dataclass
class Fighter:
    idx: int  # 0 for P1, 1 for P2
    definition: FighterDef
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    facing: int = 1  # 1 right, -1 left
    hp: int = 100
    on_ground: bool = True
    crouch: bool = False
    stun: int = 0
    attack_timer: int = 0
    attack_type: int = 0  # 0 none, 1 punch, 2 kick, 3 special
    invuln: int = 0
    wins: int = 0

    def rect(self) -> Tuple[int, int, int, int]:
        # body hitbox (approx)
        bx = int(self.x) - 6
        by = int(self.y) - (10 if self.crouch else 16)
        bw = 12
        bh = 10 if self.crouch else 16
        return bx, by, bw, bh

    def attack_rect(self) -> Optional[Tuple[int, int, int, int, int]]:
        # returns (x,y,w,h,damage) when active
        if self.attack_timer <= 0:
            return None
        if self.attack_type == 1:  # punch
            rng, dmg, ah = 12, 6, 6
        elif self.attack_type == 2:  # kick
            rng, dmg, ah = 16, 10, 7
        else:
            return None
        ax = int(self.x) + (6 if self.facing == 1 else -6 - rng)
        ay = int(self.y) - (12 if not self.crouch else 8)
        return ax, ay, rng, ah, dmg


class Game:
    def __init__(self):
        pyxel.init(W, H, title="Street Crashers", fps=60, display_scale=4)
        self._init_assets()

        self.state = STATE_TITLE
        self.menu_blink = 0

        # selections
        self.p1_sel = 0
        self.p2_sel = 1
        self.p1_locked = False
        self.p2_locked = False
        self.stage_sel = 0

        self.fighters: List[Fighter] = []
        self.projectiles: List[Projectile] = []

        self.winner_text = ""
        pyxel.run(self.update, self.draw)

    # ---------- Compatibility helpers ----------
    def enter_pressed(self) -> bool:
        """ENTER on all Pyxel versions:
        - Always uses KEY_RETURN
        - Also uses keypad enter if KEY_KP_ENTER exists in this build
        """
        if pyxel.btnp(pyxel.KEY_RETURN):
            return True
        kp = getattr(pyxel, "KEY_KP_ENTER", None)
        if kp is not None and pyxel.btnp(kp):
            return True
        return False

    def _init_assets(self):
        # Build sprites into image bank 0.
        pyxel.images[0].cls(0)
        self._draw_logo(0, 0)
        self._draw_fighter_sprites()
        self._draw_ui_icons()

        self.fighter_defs: List[FighterDef] = [
            FighterDef("Neon Ninja", 0, 32, 8, "Shuriken"),
            FighterDef("Street Brawler", 16, 32, 9, "Haymaker"),
            FighterDef("Punk Rider", 32, 32, 11, "Boomerang"),
        ]

    def _px(self, u, v, c):
        pyxel.images[0].pset(u, v, c)

    def _rect(self, u, v, w, h, c):
        pyxel.images[0].rect(u, v, w, h, c)

    def _draw_logo(self, u0, v0):
        # 128x32 bitmap-ish logo with shadow: "STREET CRASHERS"
        def draw_word(u, v, color):
            text_map = [
                " #####  #####  #####  #####  #####  #####  ",
                " #      #   #  #      #        #    #      ",
                " ####   #####  ####   ####     #    ####   ",
                "    #   #  #   #      #        #    #      ",
                " #####  #   #  #####  #####    #    #####  ",
            ]
            for y, row in enumerate(text_map):
                for x, ch in enumerate(row):
                    if ch == "#":
                        self._px(u + x, v + y, color)

        # STREET shadow + fill
        draw_word(u0 + 11, v0 + 7, 1)
        draw_word(u0 + 10, v0 + 6, 10)

        # CRASHERS
        crash = [
            "   #####   ###   #####  #   #  #####  #####  ",
            " #      #   #   #   #  #      #   #  #      #   #  ",
            " #      ####   #   #  ####   #####  ####   #####  ",
            " #      #      #   #  #      #   #  #      #  #   ",
            " #####  #   ###   #####  #   #  #####  #   #  ",
        ]
        for y, row in enumerate(crash):
            for x, ch in enumerate(row):
                if ch == "#":
                    self._px(u0 + 4 + x + 1, v0 + 18 + y + 1, 1)
        for y, row in enumerate(crash):
            for x, ch in enumerate(row):
                if ch == "#":
                    self._px(u0 + 4 + x, v0 + 18 + y, 8)

        # decorative burst behind
        for i in range(40):
            x = 64 + (i % 10) * 6
            y = 0 + (i // 10) * 3
            if (i % 2) == 0:
                self._px(u0 + x, v0 + y, 6)

    def _draw_fighter_sprites(self):
        # Each fighter: 16x16 at (u,v) = (0,32), (16,32), (32,32)
        ninja = [
            "....11111111....",
            "...11aaaaaa11...",
            "..11aaaaaaa111..",
            "..11aa1331aa11..",
            "..11aa1331aa11..",
            "..111111111111..",
            "...11b2222b11...",
            "...1bb2222bb1...",
            "...1bb2222bb1...",
            "...11b2222b11...",
            "....11c22c11....",
            "....1c2222c1....",
            "....1c2222c1....",
            "....1c.11.c1....",
            ".....11..11.....",
            ".....11..11.....",
        ]
        self._blit_pattern(0, 32, ninja, {"1": 1, "a": 8, "b": 12, "2": 1, "c": 5, "3": 7})

        brawler = [
            "....11111111....",
            "...11dddddd11...",
            "..11dd1331dd11..",
            "..11dd1331dd11..",
            "..11dddddddd11..",
            "...1111111111...",
            "...11e4444e11...",
            "..11ee4444ee11..",
            "..11e444444e11..",
            "...11e4444e11...",
            "....11f44f11....",
            "....1f4444f1....",
            "....1f4444f1....",
            "....1f.11.f1....",
            ".....11..11.....",
            ".....11..11.....",
        ]
        self._blit_pattern(16, 32, brawler, {"1": 1, "d": 9, "e": 10, "4": 3, "f": 2, "3": 7})

        punk = [
            "....11111111....",
            "...11gggggg11...",
            "..11gg1331gg11..",
            "..11gg1331gg11..",
            "..11gggggggg11..",
            "...1111111111...",
            "...11h6666h11...",
            "..11hh6666hh11..",
            "..11h666666h11..",
            "...11h6666h11...",
            "....11i66i11....",
            "....1i6666i1....",
            "....1i6666i1....",
            "....1i.11.i1....",
            ".....11..11.....",
            ".....11..11.....",
        ]
        self._blit_pattern(32, 32, punk, {"1": 1, "g": 11, "h": 14, "6": 4, "i": 12, "3": 7})

        # Shuriken (8x8)
        s = [
            "..1..1..",
            ".11.11..",
            "..111...",
            "1111111.",
            "..111...",
            ".11.11..",
            "..1..1..",
            "...11...",
        ]
        self._blit_pattern(0, 48, s, {"1": 7})

        # Boomerang (8x8)
        b = [
            "111.....",
            "1.11....",
            "1..11...",
            "1...11..",
            "1....11.",
            "1.....11",
            "1......1",
            "11.....1",
        ]
        self._blit_pattern(8, 48, b, {"1": 10})

    def _draw_ui_icons(self):
        for x in range(8):
            self._px(24 + x, 48, 7)
            self._px(24 + x, 55, 7)
        for y in range(8):
            self._px(24, 48 + y, 7)
            self._px(31, 48 + y, 7)

    def _blit_pattern(self, u0, v0, rows, cmap):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == ".":
                    continue
                c = cmap.get(ch, 0)
                if c != 0:
                    self._px(u0 + x, v0 + y, c)

    # ---------------------- Flow ----------------------

    def reset_selections(self):
        self.p1_sel, self.p2_sel = 0, 1
        self.p1_locked = False
        self.p2_locked = False
        self.stage_sel = 0

    def start_fight(self):
        d1 = self.fighter_defs[self.p1_sel]
        d2 = self.fighter_defs[self.p2_sel]
        self.fighters = [
            Fighter(0, d1, 72, GROUND_Y),
            Fighter(1, d2, W - 72, GROUND_Y),
        ]
        self.projectiles = []
        self.state = STATE_FIGHT
        self.winner_text = ""

    # ---------------------- Update ----------------------

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.state == STATE_TITLE:
            self._update_title()
        elif self.state == STATE_CHAR_SELECT:
            self._update_char_select()
        elif self.state == STATE_STAGE_SELECT:
            self._update_stage_select()
        elif self.state == STATE_FIGHT:
            self._update_fight()
        elif self.state == STATE_GAME_OVER:
            self._update_game_over()

        self.menu_blink = (self.menu_blink + 1) % 60

    def _update_title(self):
        if self.enter_pressed():
            self.reset_selections()
            self.state = STATE_CHAR_SELECT

    def _update_char_select(self):
        # P1 cursor
        if not self.p1_locked:
            if pyxel.btnp(pyxel.KEY_A):
                self.p1_sel = (self.p1_sel - 1) % len(self.fighter_defs)
            if pyxel.btnp(pyxel.KEY_D):
                self.p1_sel = (self.p1_sel + 1) % len(self.fighter_defs)
            if self.enter_pressed():
                self.p1_locked = True

        # P2 cursor
        if not self.p2_locked:
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.p2_sel = (self.p2_sel - 1) % len(self.fighter_defs)
            if pyxel.btnp(pyxel.KEY_RIGHT):
                self.p2_sel = (self.p2_sel + 1) % len(self.fighter_defs)
            if self.enter_pressed():
                self.p2_locked = True

        if self.p1_locked and self.p2_locked:
            self.state = STATE_STAGE_SELECT

    def _update_stage_select(self):
        if pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.KEY_LEFT):
            self.stage_sel = (self.stage_sel - 1) % len(STAGES)
        if pyxel.btnp(pyxel.KEY_D) or pyxel.btnp(pyxel.KEY_RIGHT):
            self.stage_sel = (self.stage_sel + 1) % len(STAGES)
        if self.enter_pressed():
            self.start_fight()

    def _input_for(self, f: Fighter):
        if f.stun > 0:
            return {
                "left": False,
                "right": False,
                "jump": False,
                "crouch": False,
                "punch": False,
                "kick": False,
                "special": False,
            }

        if f.idx == 0:
            return {
                "left": pyxel.btn(pyxel.KEY_A),
                "right": pyxel.btn(pyxel.KEY_D),
                "jump": pyxel.btnp(pyxel.KEY_W),
                "crouch": pyxel.btn(pyxel.KEY_S),
                "punch": pyxel.btnp(pyxel.KEY_J),
                "kick": pyxel.btnp(pyxel.KEY_K),
                "special": pyxel.btnp(pyxel.KEY_U),
            }
        else:
            return {
                "left": pyxel.btn(pyxel.KEY_LEFT),
                "right": pyxel.btn(pyxel.KEY_RIGHT),
                "jump": pyxel.btnp(pyxel.KEY_UP),
                "crouch": pyxel.btn(pyxel.KEY_DOWN),
                "punch": pyxel.btnp(pyxel.KEY_N),
                "kick": pyxel.btnp(pyxel.KEY_M),
                "special": pyxel.btnp(pyxel.KEY_COMMA),
            }

    def _update_fight(self):
        f1, f2 = self.fighters

        if f1.x < f2.x:
            f1.facing, f2.facing = 1, -1
        else:
            f1.facing, f2.facing = -1, 1

        for f in self.fighters:
            inp = self._input_for(f)
            f.crouch = inp["crouch"] and f.on_ground

            speed = 1.4 if not f.crouch else 0.8
            f.vx = 0.0
            if inp["left"]:
                f.vx -= speed
            if inp["right"]:
                f.vx += speed

            if inp["jump"] and f.on_ground and not f.crouch:
                f.vy = -4.4
                f.on_ground = False

            if f.attack_timer <= 0:
                if inp["punch"]:
                    f.attack_type = 1
                    f.attack_timer = 10
                elif inp["kick"]:
                    f.attack_type = 2
                    f.attack_timer = 14
                elif inp["special"]:
                    if f.invuln == 0:
                        f.attack_type = 3
                        f.attack_timer = 18
                        self._spawn_projectile(f)
                        f.invuln = 40

            if f.stun > 0:
                f.stun -= 1
            if f.attack_timer > 0:
                f.attack_timer -= 1
                if f.attack_timer == 0:
                    f.attack_type = 0
            if f.invuln > 0:
                f.invuln -= 1

            f.x += f.vx
            if not f.on_ground:
                f.vy += 0.22
            f.y += f.vy

            if f.y >= GROUND_Y:
                f.y = GROUND_Y
                f.vy = 0
                f.on_ground = True

            f.x = max(16, min(W - 16, f.x))

        if abs(f1.x - f2.x) < 14:
            mid = (f1.x + f2.x) / 2
            f1.x = mid - 7
            f2.x = mid + 7

        self._resolve_melee_hits()
        self._update_projectiles()

        if f1.hp <= 0 or f2.hp <= 0:
            if f1.hp <= 0 and f2.hp <= 0:
                self.winner_text = "DOUBLE KO!"
            elif f1.hp <= 0:
                self.winner_text = "P2 WINS!"
            else:
                self.winner_text = "P1 WINS!"
            self.state = STATE_GAME_OVER

    def _spawn_projectile(self, f: Fighter):
        dirx = 3.2 * f.facing
        py = int(f.y) - 12
        px = int(f.x) + (10 if f.facing == 1 else -10)
        self.projectiles.append(Projectile(px, py, dirx, f.idx))

    def _rects_overlap(self, a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)

    def _resolve_melee_hits(self):
        f1, f2 = self.fighters
        for attacker, defender in ((f1, f2), (f2, f1)):
            ar = attacker.attack_rect()
            if not ar:
                continue
            ax, ay, aw, ah, dmg = ar
            if defender.invuln > 0:
                continue
            if self._rects_overlap((ax, ay, aw, ah), defender.rect()):
                defender.hp = max(0, defender.hp - dmg)
                defender.stun = 10 if attacker.attack_type == 1 else 14
                defender.vx += 1.8 * attacker.facing
                defender.invuln = 18

    def _update_projectiles(self):
        f1, f2 = self.fighters
        alive = []
        for p in self.projectiles:
            p.x += p.vx
            p.life -= 1
            if p.life <= 0 or p.x < -10 or p.x > W + 10:
                continue

            target = f2 if p.owner == 0 else f1
            if target.invuln == 0 and self._rects_overlap((int(p.x), int(p.y), p.w, p.h), target.rect()):
                target.hp = max(0, target.hp - 12)
                target.stun = 16
                target.invuln = 24
                continue
            alive.append(p)
        self.projectiles = alive

    def _update_game_over(self):
        if self.enter_pressed():
            self.state = STATE_TITLE

    # ---------------------- Draw ----------------------

    def draw(self):
        if self.state == STATE_TITLE:
            self._draw_stage_bg(0, as_menu=True)
            self._draw_title()
        elif self.state == STATE_CHAR_SELECT:
            self._draw_stage_bg(0, as_menu=True)
            self._draw_char_select()
        elif self.state == STATE_STAGE_SELECT:
            self._draw_stage_bg(0, as_menu=True)
            self._draw_stage_select()
        elif self.state == STATE_FIGHT:
            self._draw_stage_bg(self.stage_sel, as_menu=False)
            self._draw_fight()
        elif self.state == STATE_GAME_OVER:
            self._draw_stage_bg(self.stage_sel, as_menu=False)
            self._draw_fight()
            self._draw_game_over()

    def _draw_title(self):
        pyxel.blt(64, 18, 0, 0, 0, 128, 32, 0)
        pyxel.text(78, 58, "90s ARCADE BRAWLER", 7)
        if self.menu_blink < 30:
            pyxel.text(86, 96, "PRESS ENTER", 10)
        pyxel.text(8, 134, "P1: A/D + ENTER   P2: \x1b/\x1a + ENTER", 6)

    def _draw_char_select(self):
        pyxel.text(88, 10, "CHARACTER SELECTION", 7)
        pyxel.text(20, 26, "P1", 8)
        pyxel.text(220, 26, "P2", 9)

        for i, fd in enumerate(self.fighter_defs):
            x = 48 + i * 64
            pyxel.rect(x - 18, 44, 36, 52, 1)
            pyxel.rect(x - 17, 45, 34, 50, 0)
            pyxel.blt(x - 8, 54, 0, fd.sprite_u, fd.sprite_v, 16, 16, 0)
            pyxel.text(x - 16, 74, fd.name[:10], 7)
            pyxel.text(x - 16, 82, fd.special_name, fd.accent_color)

        cx1 = 48 + self.p1_sel * 64
        cx2 = 48 + self.p2_sel * 64

        ccol1 = 8 if not self.p1_locked else 11
        pyxel.rectb(cx1 - 22, 40, 44, 60, ccol1)
        pyxel.text(cx1 - 10, 102, "READY" if self.p1_locked else "PICK", ccol1)

        ccol2 = 9 if not self.p2_locked else 11
        pyxel.rectb(cx2 - 22, 40, 44, 60, ccol2)
        pyxel.text(cx2 - 10, 112, "READY" if self.p2_locked else "PICK", ccol2)

        pyxel.text(58, 130, "ENTER to lock-in (both players)", 6)

    def _draw_stage_select(self):
        pyxel.text(94, 10, "STAGE SELECTION", 7)
        for i, (name, desc) in enumerate(STAGES):
            x = 20
            y = 34 + i * 28
            col = 10 if i == self.stage_sel else 7
            pyxel.rect(x, y, 216, 22, 1)
            pyxel.rect(x + 1, y + 1, 214, 20, 0)
            pyxel.text(x + 6, y + 6, name, col)
            pyxel.text(x + 100, y + 6, desc, 6)
        pyxel.text(46, 128, "A/D or \x1b/\x1a to choose, ENTER to fight!", 6)

    def _draw_fight(self):
        for f in self.fighters:
            self._draw_fighter(f)

        for p in self.projectiles:
            if p.owner == 0:
                pyxel.blt(int(p.x), int(p.y), 0, 0, 48, 8, 8, 0)
            else:
                pyxel.blt(int(p.x), int(p.y), 0, 8, 48, 8, 8, 0)

        self._draw_hud()

    def _draw_game_over(self):
        pyxel.rect(78, 52, 100, 40, 1)
        pyxel.rect(79, 53, 98, 38, 0)
        pyxel.text(104, 62, self.winner_text, 10)
        pyxel.text(86, 78, "PRESS ENTER", 7)

    def _draw_hud(self):
        f1, f2 = self.fighters
        self._hp_bar(16, 10, f1.hp, 8, "P1")
        self._hp_bar(W - 16 - 96, 10, f2.hp, 9, "P2")
        pyxel.text(104, 10, STAGES[self.stage_sel][0], 7)

    def _hp_bar(self, x, y, hp, col, label):
        pyxel.text(x, y - 8, label, col)
        pyxel.rect(x, y, 96, 8, 1)
        fill = int(96 * max(0, hp) / 100)
        pyxel.rect(x + 1, y + 1, max(0, fill - 2), 6, col)
        pyxel.rect(x + 1 + max(0, fill - 2), y + 1, max(0, 96 - fill), 6, 0)

    def _draw_fighter(self, f: Fighter):
        u, v = f.definition.sprite_u, f.definition.sprite_v
        x = int(f.x) - 8
        y = int(f.y) - 16
        if f.facing == 1:
            pyxel.blt(x, y, 0, u, v, 16, 16, 0)
        else:
            pyxel.blt(x, y, 0, u + 15, v, -16, 16, 0)

        if f.attack_timer > 0 and f.attack_type in (1, 2):
            ar = f.attack_rect()
            if ar:
                ax, ay, aw, ah, _ = ar
                pyxel.rectb(ax, ay, aw, ah, f.definition.accent_color)

        if f.invuln > 0 and (pyxel.frame_count // 3) % 2 == 0:
            pyxel.rectb(*f.rect(), 7)

    # ---------------------- Stage backgrounds ----------------------

    def _draw_stage_bg(self, idx: int, as_menu: bool):
        pyxel.cls(0)
        if idx == 0:
            self._bg_parking_lot(as_menu)
        elif idx == 1:
            self._bg_rooftop(as_menu)
        else:
            self._bg_subway(as_menu)

    def _bg_parking_lot(self, as_menu: bool):
        pyxel.rect(0, 0, W, H, 1)
        for i in range(40):
            x = (i * 17 + pyxel.frame_count) % W
            y = (i * 7) % 50
            pyxel.pset(x, y, 6 if i % 2 == 0 else 5)

        pyxel.rect(40, 46, 176, 52, 0)
        pyxel.rectb(40, 46, 176, 52, 7)
        pyxel.rect(40, 46, 176, 10, 12)
        pyxel.text(112, 52, "DINER", 10)
        pyxel.text(140, 52, "BURGER", 8)

        pyxel.rect(188, 24, 52, 40, 0)
        pyxel.rectb(188, 24, 52, 40, 11)
        pyxel.text(197, 32, "Diner", 8)
        pyxel.text(196, 42, "OPEN", 10)

        for x in (30, 92, 152, 210):
            pyxel.rect(x, 94, 36, 12, 2)
            pyxel.rect(x + 4, 90, 28, 6, 2)
            pyxel.rect(x + 6, 92, 8, 3, 0)
            pyxel.rect(x + 18, 92, 8, 3, 0)
            pyxel.circ(x + 8, 106, 3, 0)
            pyxel.circ(x + 28, 106, 3, 0)

        pyxel.rect(0, GROUND_Y, W, H - GROUND_Y, 3)
        for i in range(5):
            lx = (i * 52 + (pyxel.frame_count // 2)) % W
            pyxel.elli(lx, GROUND_Y + 16, 24, 10, 10 if i % 2 == 0 else 9)

        if not as_menu:
            for x in range(0, W, 14):
                pyxel.rect(x, GROUND_Y + 10, 7, 2, 7)

    def _bg_rooftop(self, as_menu: bool):
        pyxel.rect(0, 0, W, H, 1)
        for i in range(80):
            x = (i * 19) % W
            y = (i * 11) % 70
            if (i + pyxel.frame_count) % 17 == 0:
                pyxel.pset(x, y, 7)
        for i in range(18):
            x = i * 16
            hh = 20 + (i * 13) % 50
            pyxel.rect(x, 78 - hh, 14, hh, 2)
            for wy in range(78 - hh + 4, 78, 7):
                pyxel.rect(x + 3, wy, 2, 2, 10)
                pyxel.rect(x + 8, wy + 2, 2, 2, 8)
        pyxel.rect(0, GROUND_Y, W, H - GROUND_Y, 5)
        pyxel.rect(0, GROUND_Y - 18, W, 18, 0)
        pyxel.text(8, 96, "ROOFTOP RUMBLE", 10 if as_menu else 6)

    def _bg_subway(self, as_menu: bool):
        pyxel.rect(0, 0, W, H, 0)
        pyxel.rect(0, 0, W, 86, 1)
        for x in range(20, W, 42):
            pyxel.rect(x, 40, 10, 60, 2)
            pyxel.rect(x - 2, 40, 14, 6, 3)
        pyxel.rect(0, GROUND_Y - 10, W, 10, 4)
        pyxel.rect(0, GROUND_Y, W, H - GROUND_Y, 3)
        pyxel.rect(68, 16, 120, 16, 2)
        pyxel.rectb(68, 16, 120, 16, 7)
        pyxel.text(82, 21, "SUBWAY SLAM", 10 if as_menu else 7)
        for i in range(10):
            x = (i * 26 + pyxel.frame_count) % W
            pyxel.pset(x, 84, 10 if i % 2 == 0 else 8)


if __name__ == "__main__":
    Game()
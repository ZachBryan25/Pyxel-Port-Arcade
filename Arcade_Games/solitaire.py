import pyxel
import random

W, H = 320, 240
CARD_W = 20
CARD_H = 28
TABLEAU_GAP_Y = 10

STOCK_X, STOCK_Y = 10, 10
WASTE_X, WASTE_Y = 40, 10
FOUNDATION_X_START, FOUNDATION_Y = 180, 10
TABLEAU_X_START, TABLEAU_Y = 10, 60
PILE_SPACING_X = 30


class Card:
    def __init__(self, suit, rank):
        self.suit = suit          # "H", "D", "C", "S"
        self.rank = rank          # 1-13
        self.face_up = False

    def is_red(self):
        return self.suit in ["H", "D"]

    def label(self):
        return rank_to_text(self.rank) + suit_symbol(self.suit)


def rank_to_text(rank):
    if rank == 1:
        return "A"
    if rank == 11:
        return "J"
    if rank == 12:
        return "Q"
    if rank == 13:
        return "K"
    return str(rank)


def suit_symbol(suit):
    return {
        "H": "♥",
        "D": "♦",
        "C": "♣",
        "S": "♠"
    }[suit]


class App:
    def __init__(self):
        pyxel.init(W, H, title="Pyxel Solitaire")
        pyxel.mouse(True)

        self.reset_game()

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.stock = []
        self.waste = []
        self.foundations = [[], [], [], []]
        self.tableau = [[] for _ in range(7)]

        self.selected_cards = None
        self.selected_source = None
        self.message = ""
        self.win = False

        deck = self.create_deck()

        # Deal tableau
        for col in range(7):
            for row in range(col + 1):
                card = deck.pop()
                if row == col:
                    card.face_up = True
                self.tableau[col].append(card)

        self.stock = deck

    def create_deck(self):
        suits = ["H", "D", "C", "S"]
        deck = [Card(suit, rank) for suit in suits for rank in range(1, 14)]
        random.shuffle(deck)
        return deck

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.reset_game()
            return

        if self.check_win():
            self.win = True

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx = pyxel.mouse_x
            my = pyxel.mouse_y
            self.handle_click(mx, my)

    def handle_click(self, mx, my):
        self.message = ""

        # stock click
        if self.point_in_rect(mx, my, STOCK_X, STOCK_Y, CARD_W, CARD_H):
            if self.selected_cards is None:
                self.draw_from_stock()
            else:
                self.clear_selection()
            return

        # waste click
        if self.point_in_rect(mx, my, WASTE_X, WASTE_Y, CARD_W, CARD_H):
            if self.waste:
                if self.selected_cards is None:
                    self.select_waste()
                else:
                    self.try_move_to_waste()
            return

        # foundation clicks
        for i in range(4):
            fx = FOUNDATION_X_START + i * PILE_SPACING_X
            fy = FOUNDATION_Y
            if self.point_in_rect(mx, my, fx, fy, CARD_W, CARD_H):
                if self.selected_cards is None:
                    self.select_foundation(i)
                else:
                    self.try_move_to_foundation(i)
                return

        # tableau clicks
        for col in range(7):
            result = self.get_tableau_clicked(col, mx, my)
            if result is not None:
                clicked_index = result
                if self.selected_cards is None:
                    self.select_tableau(col, clicked_index)
                else:
                    self.try_move_to_tableau(col)
                return

        # empty tableau click area
        for col in range(7):
            tx = TABLEAU_X_START + col * PILE_SPACING_X
            ty = TABLEAU_Y
            empty_h = CARD_H if not self.tableau[col] else CARD_H + (len(self.tableau[col]) - 1) * TABLEAU_GAP_Y
            if self.point_in_rect(mx, my, tx, ty, CARD_W, empty_h):
                if self.selected_cards is not None:
                    self.try_move_to_tableau(col)
                    return

        self.clear_selection()

    def draw_from_stock(self):
        if self.stock:
            card = self.stock.pop()
            card.face_up = True
            self.waste.append(card)
        else:
            while self.waste:
                card = self.waste.pop()
                card.face_up = False
                self.stock.append(card)

    def select_waste(self):
        if self.waste:
            self.selected_cards = [self.waste[-1]]
            self.selected_source = ("waste", None)

    def select_foundation(self, foundation_index):
        pile = self.foundations[foundation_index]
        if pile:
            self.selected_cards = [pile[-1]]
            self.selected_source = ("foundation", foundation_index)

    def select_tableau(self, col, index):
        pile = self.tableau[col]
        if index < 0 or index >= len(pile):
            return

        if not pile[index].face_up:
            return

        self.selected_cards = pile[index:]
        self.selected_source = ("tableau", col, index)

    def try_move_to_foundation(self, foundation_index):
        if self.selected_cards is None:
            return

        if len(self.selected_cards) != 1:
            self.message = "Only one card to foundation"
            return

        card = self.selected_cards[0]
        foundation = self.foundations[foundation_index]

        if self.valid_foundation_move(card, foundation):
            self.remove_selected_from_source()
            self.foundations[foundation_index].append(card)
            self.after_tableau_move_cleanup()
            self.clear_selection()
        else:
            self.message = "Invalid foundation move"

    def try_move_to_tableau(self, col):
        if self.selected_cards is None:
            return

        dest_pile = self.tableau[col]
        first_card = self.selected_cards[0]

        if self.selected_source and self.selected_source[0] == "tableau":
            src_col = self.selected_source[1]
            if src_col == col:
                self.clear_selection()
                return

        if self.valid_tableau_move(first_card, dest_pile):
            moved_cards = self.selected_cards[:]
            self.remove_selected_from_source()
            self.tableau[col].extend(moved_cards)
            self.after_tableau_move_cleanup()
            self.clear_selection()
        else:
            self.message = "Invalid tableau move"

    def try_move_to_waste(self):
        self.message = "Cannot move onto waste"

    def remove_selected_from_source(self):
        if self.selected_source is None or self.selected_cards is None:
            return

        source_type = self.selected_source[0]

        if source_type == "waste":
            self.waste.pop()

        elif source_type == "foundation":
            foundation_index = self.selected_source[1]
            self.foundations[foundation_index].pop()

        elif source_type == "tableau":
            col = self.selected_source[1]
            index = self.selected_source[2]
            self.tableau[col] = self.tableau[col][:index]

    def after_tableau_move_cleanup(self):
        if self.selected_source and self.selected_source[0] == "tableau":
            src_col = self.selected_source[1]
            if self.tableau[src_col]:
                if not self.tableau[src_col][-1].face_up:
                    self.tableau[src_col][-1].face_up = True

    def clear_selection(self):
        self.selected_cards = None
        self.selected_source = None

    def valid_foundation_move(self, card, foundation):
        if not foundation:
            return card.rank == 1

        top = foundation[-1]
        return card.suit == top.suit and card.rank == top.rank + 1

    def valid_tableau_move(self, card, dest_pile):
        if not dest_pile:
            return card.rank == 13

        top = dest_pile[-1]
        if not top.face_up:
            return False

        return (card.is_red() != top.is_red()) and (card.rank == top.rank - 1)

    def check_win(self):
        return all(len(f) == 13 for f in self.foundations)

    def get_tableau_clicked(self, col, mx, my):
        pile = self.tableau[col]
        x = TABLEAU_X_START + col * PILE_SPACING_X
        y = TABLEAU_Y

        if not pile:
            if self.point_in_rect(mx, my, x, y, CARD_W, CARD_H):
                return None
            return None

        for i in range(len(pile) - 1, -1, -1):
            cy = y + i * TABLEAU_GAP_Y
            h = CARD_H if i == len(pile) - 1 else TABLEAU_GAP_Y + 2
            if self.point_in_rect(mx, my, x, cy, CARD_W, h):
                return i

        return None

    def point_in_rect(self, px, py, x, y, w, h):
        return x <= px < x + w and y <= py < y + h

    def draw_card(self, x, y, card, selected=False):
        if card.face_up:
            pyxel.rect(x, y, CARD_W, CARD_H, 7)

            border = 10 if selected else 0
            pyxel.rectb(x, y, CARD_W, CARD_H, border)

            rank = rank_to_text(card.rank)
            suit = suit_symbol(card.suit)
            color = 8 if card.is_red() else 0

            pyxel.text(x + 2, y + 2, rank, color)
            pyxel.text(x + 2, y + 10, suit, color)

            pyxel.text(x + CARD_W - 10, y + CARD_H - 10, rank, color)
            pyxel.text(x + CARD_W - 10, y + CARD_H - 18, suit, color)

        else:
            pyxel.rect(x, y, CARD_W, CARD_H, 5)
            pyxel.rectb(x, y, CARD_W, CARD_H, 0)
            pyxel.text(x + 5, y + 10, "[]", 1)

    def draw_empty_slot(self, x, y):
        pyxel.rectb(x, y, CARD_W, CARD_H, 6)

    def draw(self):
        pyxel.cls(3)

        pyxel.text(10, 2, "STOCK", 7)
        pyxel.text(40, 2, "WASTE", 7)
        pyxel.text(180, 2, "FOUNDATIONS", 7)

        if self.stock:
            pyxel.rect(STOCK_X, STOCK_Y, CARD_W, CARD_H, 5)
            pyxel.rectb(STOCK_X, STOCK_Y, CARD_W, CARD_H, 0)
            pyxel.text(STOCK_X + 3, STOCK_Y + 10, "[]", 1)
        else:
            self.draw_empty_slot(STOCK_X, STOCK_Y)

        if self.waste:
            selected = self.selected_source == ("waste", None)
            self.draw_card(WASTE_X, WASTE_Y, self.waste[-1], selected)
        else:
            self.draw_empty_slot(WASTE_X, WASTE_Y)

        for i in range(4):
            x = FOUNDATION_X_START + i * PILE_SPACING_X
            y = FOUNDATION_Y
            pile = self.foundations[i]
            if pile:
                selected = self.selected_source == ("foundation", i)
                self.draw_card(x, y, pile[-1], selected)
            else:
                self.draw_empty_slot(x, y)

        for col in range(7):
            x = TABLEAU_X_START + col * PILE_SPACING_X
            y = TABLEAU_Y
            pile = self.tableau[col]

            if not pile:
                self.draw_empty_slot(x, y)
                continue

            for i, card in enumerate(pile):
                cy = y + i * TABLEAU_GAP_Y

                selected = False
                if self.selected_source and self.selected_source[0] == "tableau":
                    src_col = self.selected_source[1]
                    src_index = self.selected_source[2]
                    if src_col == col and i >= src_index:
                        selected = True

                self.draw_card(x, cy, card, selected)

        pyxel.text(10, 220, "Click cards to select/move | R = restart", 7)

        if self.message:
            pyxel.text(10, 230, self.message, 8)

        if self.win:
            pyxel.rect(90, 100, 140, 30, 0)
            pyxel.rectb(90, 100, 140, 30, 10)
            pyxel.text(132, 112, "YOU WIN!", 11)


App()
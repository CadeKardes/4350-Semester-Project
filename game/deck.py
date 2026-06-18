import random

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

VALUES = [
    ("2", 2),
    ("3", 3),
    ("4", 4),
    ("5", 5),
    ("6", 6),
    ("7", 7),
    ("8", 8),
    ("9", 9),
    ("10", 10),
    ("Jack", 11),
    ("Queen", 12),
    ("King", 13),
    ("Ace", 14)
]


class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()
        self.shuffle()

    def create_deck(self):
        for suit in SUITS:
            for name, value in VALUES:
                self.cards.append({
                    "suit": suit,
                    "name": name,
                    "value": value,
                    "color": "Red" if suit in ["Hearts", "Diamonds"] else "Black"
                })

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if len(self.cards) == 0:
            return None

        return self.cards.pop()
import random

SUITS = ['\u2660', '\u2665', '\u2666', '\u2663']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
RANK_VAL = {
    'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13
}

def build_deck():
    """Build and return a shuffled 52-card deck."""
    deck = [{'rank': r, 'suit': s, 'val': RANK_VAL[r]} for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

def is_red(card):
    """Return True if the card is a red suit (hearts or diamonds)."""
    return card['suit'] in ['\u2665', '\u2666']

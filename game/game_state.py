from game.deck import Deck

class GameState:

    def __init__(self):
        self.reset()

    def reset(self):

        self.deck = Deck()

        self.round = 1

        self.cards = []

        self.game_over = False
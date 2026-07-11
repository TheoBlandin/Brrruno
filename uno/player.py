class Player:
    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.hand = []
        self.draw = False

    def add_card(self, card):
        self.hand.append(card)

    def play_card(self, card):
        self.hand.remove(card)
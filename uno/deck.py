import random
from collections import deque

class Deck:
    def __init__(self):
        self.cards = []

    def build(self):
        colors = ["🟥 rouge", "🟩 vert", "🟦 bleu", "🟨 jaune"]

        for c in colors:
            # Carte numérotées
            for i in range(10):
                # Il y a deux cartes de chaque chiffre de 1 à 9 par couleur, mais un seul exemplaire de 0
                self.cards.append(f"{c}_{i}")
                if i != 0:
                    self.cards.append(f"{c}_{i}")

            # Cartes spéciales
            self.cards += [f"{c}_passeTonTour", f"{c}_changeDeSens", f"{c}_+2"] * 2

        # Cartes jokers
        self.cards += [f"⬛ joker", f"⬛ joker_+4"] * 4

        self.cards = deque(self.cards)

        # Mélanger le paquet
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop() # Enlever la dernière carte du paquet
    
    def add(self, card):
        return self.cards.appendleft(card)
    

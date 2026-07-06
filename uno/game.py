from uno.deck import Deck
from uno.player import Player


class Uno:
    def __init__(self):
        self.players = []
        self.started = False

        self.deck = Deck()
        self.current_card = None

    def add_player(self, pseudo):
        if self.started: # Partie déjà en cours
            return (False, "ALREADY_STARTED")
        
        if pseudo in self.players: # Joueur déjà enregistré
            return (False, "ALREADY_IN")
        
        self.players.append(Player(pseudo))
        return (True, "OK")
    
    def remove_player(self, pseudo):
        if self.started: # Partie déjà en cours
            return (False, "ALREADY_STARTED")
        
        if pseudo not in self.players: # Joueur non enregistré
            return (False, "NOT_IN")
        
        self.players.pop(self.players.index(Player(pseudo)))
        return (True, "OK")
    
    def see_players(self):
        return self.players
    
    def start_game(self):
        if self.started: # Partie déjà en cours
            return (False, "ALREADY_STARTED")
        
        if len(self.players) < 2: # Pas assez de joueurs
            return (False, "NOT_ENOUGH")
        
        self.started = True
        self.deck.build()

        # Distribuer 7 cartes par joueur
        for p in self.players:
            for _ in range(7) : 
                p.add_card(self.deck.draw())

        self.current_card = self.deck.draw() # Première carte de la partie

        return (True, "OK")
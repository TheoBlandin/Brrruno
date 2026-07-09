from uno.deck import Deck
from uno.player import Player

FORBIDDEN_START = [f"⬛ joker", f"⬛ joker_+4", f"🟥 rouge_passeTonTour", f"🟩 vert_passeTonTour", f"🟦 bleu_passeTonTour", f"🟨 jaune_passeTonTour", f"🟥 rouge_changeDeSens", f"🟩 vert_changeDeSens", f"🟦 bleu_changeDeSens", f"🟨 jaune_changeDeSens", f"🟥 rouge_+2", f"🟩 vert_+2", f"🟦 bleu_+2", f"🟨 jaune_+2"]

class Uno:
    def __init__(self):
        self.players = []
        self.started = False

        self.deck = Deck()
        self.current_card = None

        self.current_player = 0

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
        while self.current_card in FORBIDDEN_START :
            self.deck.add(self.current_card) # Remettre la carte dans le paquet
            self.current_card = self.deck.draw() 

        return (True, "OK")
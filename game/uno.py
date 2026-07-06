class Uno:
    def __init__(self):
        self.players = []
        self.started = False

    def add_player(self, pseudo):
        if self.started: # Partie déjà en cours
            return False
        
        if pseudo in self.players: # Joueur déjà enregistré
            return False
        
        self.players.append(pseudo)
        return True
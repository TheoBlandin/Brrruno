class Uno:
    def __init__(self):
        self.players = []
        self.started = False

    def add_player(self, pseudo):
        if self.started: # Partie déjà en cours
            return (False, "ALREADY_STARTED")
        
        if pseudo in self.players: # Joueur déjà enregistré
            return (False, "ALREADY_IN")
        
        self.players.append(pseudo)
        return (True, "OK")
    
    def see_players(self):
        return self.players
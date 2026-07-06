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
    
    def remove_player(self, pseudo):
        if self.started: # Partie déjà en cours
            return (False, "ALREADY_STARTED")
        
        if pseudo not in self.players: # Joueur non enregistré
            return (False, "NOT_IN")
        
        self.players.pop(self.players.index(pseudo))
        return (True, "OK")
    
    def see_players(self):
        return self.players
    
    def start_game(self):
        if self.started: # Partie déjà en cours
            return (False, "ALREADY_STARTED")
        
        if len(self.players) < 2: # Pas assez de joueurs
            return (False, "NOT_ENOUGH")
        
        self.started = True
        return (True, "OK")
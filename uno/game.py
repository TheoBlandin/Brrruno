from uno.deck import Deck
from uno.player import Player
from utils.rules import checkPlay

FORBIDDEN_START = [f"joker", f"joker_+4", f"rouge_passeTonTour", f"vert_passeTonTour", f"bleu_passeTonTour", f"jaune_passeTonTour",
                   f"rouge_changeDeSens", f"vert_changeDeSens", f"bleu_changeDeSens", f"jaune_changeDeSens", f"rouge_+2", f"vert_+2", f"bleu_+2", f"jaune_+2"]


class Uno:
    def __init__(self):
        self.players = []
        self.started = False

        self.deck = Deck()

        self.current_card = None
        self.current_player = 0

        self.direction = 1

    def add_player(self, pseudo):
        if self.started:  # Partie déjà en cours
            return (False, "ALREADY_STARTED")

        if pseudo in self.players:  # Joueur déjà enregistré
            return (False, "ALREADY_IN")

        self.players.append(Player(pseudo))
        return (True, "OK")

    def remove_player(self, pseudo):
        if self.started:  # Partie déjà en cours
            return (False, "ALREADY_STARTED")

        if pseudo not in self.players:  # Joueur non enregistré
            return (False, "NOT_IN")

        self.players.pop(self.players.index(Player(pseudo)))
        return (True, "OK")

    def see_players(self):
        return self.players

    def start_game(self):
        if self.started:  # Partie déjà en cours
            return (False, "ALREADY_STARTED")

        if len(self.players) < 2:  # Pas assez de joueurs
            return (False, "NOT_ENOUGH")

        self.started = True
        self.deck.build()

        # Distribuer 7 cartes par joueur
        for p in self.players:
            for _ in range(7):
                p.add_card(self.deck.draw())

        self.current_card = self.deck.draw()  # Première carte de la partie
        # Les cartes spéciales ne peuvent pas démarrer la partie
        while self.current_card in FORBIDDEN_START:
            # Remettre la carte dans le paquet
            self.deck.add(self.current_card)
            self.current_card = self.deck.draw()

        return (True, "OK")

    def play(self, pseudo, msg):
        # La partie n'a pas encore commencé
        if not self.started:
            return (False, "NOT_STARTED")

        # Ce n'est pas à ce joueur de jouer
        if self.players[self.current_player].pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        # Le joueur ne possède pas sa carte dans sa main
        player = self.players[self.current_player]
        card = msg.split()[1]
        if card not in player.hand:
            return (False, "NOT_IN_HAND")

        # Vérifier la validité du coup
        check, message = checkPlay(self, card)
        if not check:
            return (check, message)

        # Gestion des cartes spéciales
        _, card_symbol = card.split('_')
        if card_symbol == "changeDeSens":
            self.direction *= -1

        elif card_symbol == "passeTonTour":
            self.next_player()  # Passer directement le tour du joueur suivant

        # Tour suivant
        player.play_card(card)  # Retirer la carte de la main du joueur
        self.current_card = card  # Mettre à jour la carte du haut du paquet
        self.next_player()  # Passer la main au joueur suivant
        return (check, message)

    def draw_card(self, pseudo):
        # La partie n'a pas encore commencé
        if not self.started:
            return (False, "NOT_STARTED")

        # Ce n'est pas à ce joueur de jouer
        if self.players[self.current_player].pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        player = self.players[self.current_player]
        player.add_card(self.deck.draw())
        return (True, "OK")

    def next_player(self):
        self.current_player = (self.current_player +
                               self.direction) % len(self.players)

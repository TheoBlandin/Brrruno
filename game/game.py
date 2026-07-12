from game.deck import Deck
from game.player import Player
from utils.colors import COLORS
from utils.rules import checkPossibilityAction, checkAction

FORBIDDEN_START = [f"joker_couleurs", f"joker_+4", f"rouge_passeTonTour", f"vert_passeTonTour", f"bleu_passeTonTour", f"jaune_passeTonTour",
                   f"rouge_changeDeSens", f"vert_changeDeSens", f"bleu_changeDeSens", f"jaune_changeDeSens", f"rouge_+2", f"vert_+2", f"bleu_+2", f"jaune_+2"]


class Game:
    """ Partie de jeu de Uno

    Attributes:
        deck (Deck): Paquet de carte
        started (bool): Statut de la partie
        players (Player[]): Liste des joueurs membres de la partie
        current_player (int): Indice du joueur actuel dans le tableau players
        finish_order (str[]): Pseudo des gagnants, par ordre du plus rapide
        current_card (str): Carte sur laquelle le joueur actuel doit jouer
        direction (int): Sens du jeu, avec 1 pour le sens classique et -1 pour le sens inverse
        ask_color (bool): Flag permettant de savoir si on attend que le joueur choisisse une couleur suite à une carte Joker 
    """

    def __init__(self):
        """ Initialise la partie """

        self.deck = Deck()
        self.started = False

        self.players = []
        self.current_player = 0
        self.finish_order = []

        self.current_card = None

        self.direction = 1

        self.ask_color = False

    def add_player(self, pseudo):
        """ Ajouter un joueur dans la partie

        Parameters :
            pseudo (str): Pseudo du joueur à ajouter

        Returns:
            (bool): Succès de l'ajout du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        if self.started:  # Partie déjà en cours
            return (False, "ALREADY_STARTED")

        if pseudo in self.players:  # Joueur déjà enregistré
            return (False, "ALREADY_IN")

        self.players.append(Player(pseudo))
        return (True, "OK")

    def remove_player(self, pseudo, isCommand):
        """ Retirer un joueur de la partie

        Parameters :
            pseudo (str): Pseudo du joueur à retirer
            isCommand (bool): Source de l'appel avec True si ça provient de la commande !quit, False sinon

        Returns:
            (bool): Succès du retrait du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        if self.started and isCommand:
            return (False, "ALREADY_STARTED")

        for player in self.players:
            if player.pseudo == pseudo:
                self.players.remove(player)
                return (True, "OK")

        return (False, "NOT_IN")

    def see_players(self):
        """ Voir la liste des joueurs présents dans la partie

        Returns:
            (str[]): Liste d'objet Player
        """

        return self.players

    def start_game(self):
        """ Lancer la partie

        Returns:
            (bool): Succès du lancement de la partie
            (str): Message justificatif du succès ou de l'échec
        """

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

    async def play(self, bot, pseudo, channel, msg):
        """ Traiter l'action Jouer une carte

        Parameters:
            bot (IRCClient): Bot de jeu connecté à l'IRC
            pseudo (string): Pseudo du joueur qui a effectué l'action
            channel (string): Salon dans lequel le joueur a effectué l'action
            msg (string): Message du joueur composant son action

        Returns:
            (bool): Succès de l'action du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        # La partie n'a pas encore commencé
        if not self.started:
            return (False, "NOT_STARTED")

        # Ce n'est pas à ce joueur de jouer
        if self.players[self.current_player].pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        # Aucune carte sélectionnée
        parts = msg.split()
        if len(parts) < 2:
            return False, "NO_CARD"

        # Le joueur ne possède pas cette carte dans sa main
        player = self.players[self.current_player]
        card = parts[1]
        if card not in player.hand:
            return (False, "NOT_IN_HAND")

        # Vérifier la possibilité d'une action en fonction des règles
        check = checkAction(self, card)
        if not check:
            return (check, "INVALID")  # Cette action n'est pas possible

        player.play_card(card)  # Retirer la carte de la main du joueur

        # Gestion des cartes spéciales
        card_color, card_symbol = card.split('_')
        if card_symbol == "changeDeSens":
            self.direction *= -1
        elif card_symbol == "passeTonTour":
            self.next_player()  # Passer directement le tour du joueur suivant
        elif card_color == "joker":
            if card_symbol == "+4":  # Carte joker +4
                # Joueur qui va piocher
                next_player = self.players[(
                    self.current_player + self.direction) % len(self.players)]

                cards = []
                for _ in range(4):  # Piocher 4 cartes
                    new_card = self.deck.draw()
                    next_player.add_card(new_card)

                    cards.append(
                        COLORS[new_card.split('_')[0]] + ' ' + new_card)

                drawed_string = ", ".join(cards)

                await bot.send(f"PRIVMSG {channel} :Ouille, ça fait mal ! {next_player.pseudo} pioche 4 cartes.")

                await bot.send(f"NOTICE {next_player.pseudo} :Tu as pioché les cartes suivantes : {drawed_string}.")

            await self.asking_color(bot, channel)
            return (False, "WAIT_COLOR")
        elif card_symbol == "+2":
            # Joueur qui va piocher
            next_player = self.players[(
                self.current_player + self.direction) % len(self.players)]

            cards = []
            for _ in range(2):  # Piocher 2 cartes
                new_card = self.deck.draw()
                next_player.add_card(new_card)

                cards.append(COLORS[new_card.split('_')[0]] + ' ' + new_card)

            drawed_string = ", ".join(cards)

            await bot.send(f"PRIVMSG {channel} :Ouille, ça fait mal ! {next_player.pseudo} pioche 2 cartes.")

            await bot.send(f"NOTICE {next_player.pseudo} :Tu as pioché les cartes suivantes :  {drawed_string}.")

        if len(player.hand) == 0:  # Le joueur n'a plus de carte en main
            await bot.send(f"PRIVMSG {channel} :{player.pseudo} a terminé la partie, félicitations !")
            self.remove_player(player.pseudo, False)
            # Ajouter le joueur à la liste des gagnants
            self.finish_order.append(player.pseudo)
            if len(self.players) == 1:  # Il n'y a plus qu'un seul joueur dans la partie
                self.started = False  # Fin de la partie
                return (False, "END")

        # Tour suivant
        player.draw = False  # Réinitialiser le flag de pioche du joueur
        self.current_card = card  # Mettre à jour la carte du haut du paquet
        self.next_player()  # Passer la main au joueur suivant
        return (check, "OK")

    def draw_card(self, pseudo):
        """ Gérer l'action piocher d'un joueur

        Parameters:
            pseudo (str): Pseudo du joueur qui a effectué l'action

        Returns:
            (bool): Succès de l'action du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        # La partie n'a pas encore commencé
        if not self.started:
            return (False, "NOT_STARTED")

        # Ce n'est pas à ce joueur de jouer
        if self.players[self.current_player].pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        player = self.players[self.current_player]

        # Le joueur a déjà pioché ce tour-ci
        if player.draw:
            return (False, "ALREADY_DRAW")

        # Le joueur peut jouer sans piocher
        if checkPossibilityAction(self, player.hand):
            return (False, "MOVE_POSSIBLE")

        player.add_card(self.deck.draw())
        player.draw = True
        player.uno = False # Réinitialiser Uno

        if len(self.deck.cards) == 0:  # pioche vide
            self.deck.refill()  # Recréer une pioche avec les cartes non en jeu

        return (True, "OK")

    def next_player(self):
        """ Passer au joueur suivant """

        self.current_player = (self.current_player +
                               self.direction) % len(self.players)

    async def asking_color(self, bot, channel):
        """ Demander au joueur la couleur qu'il souhaite suite à l'usage d'une carte Joker 

        Parameters:
            bot (IRCClient): Bot de jeu connecté à l'IRC
            channel (str): Salon dans lequel le bot doit envoyer le message
        """

        await bot.send(f"PRIVMSG {channel} :Quelle nouvelle couleur choisis-tu ?")
        self.ask_color = True  # Une couleur est en attente

    async def choose_color(self, bot, pseudo, channel, msg):
        """ Traiter l'action Choisir une couleur 

        Parameters:
            pseudo (string): Pseudo du joueur qui a effectué l'action
            msg (string): Message du joueur composant son action

        Returns:
            (bool): Succès de l'action du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        # La partie n'a pas encore commencé
        if not self.started:
            return (False, "NOT_STARTED")

        # Ce n'est pas à ce joueur de jouer
        if self.players[self.current_player].pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        # La couleur n'a pas été demandée
        if not self.ask_color:
            return (False, "NOT_ASKED")

        # Construction d'une fausse carte pour la couleur et tour suivant
        self.current_card = msg.replace('!', '') + "_undefined"
        self.ask_color = False  # La couleur n'est plus demandée
        # Réinitialiser le flag de pioche du joueur
        self.players[self.current_player].draw = False
        self.next_player()  # Passer la main au joueur suivant
        return (True, "OK")

    def pass_turn(self, pseudo):
        """ Traiter l'action Passer son tour

        Parameters:
            pseudo (string): Pseudo du joueur qui a effectué l'action

        Returns:
            (bool): Succès de l'action du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        # La partie n'a pas encore commencé
        if not self.started:
            return (False, "NOT_STARTED")

        # Ce n'est pas à ce joueur de jouer
        if self.players[self.current_player].pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        player = self.players[self.current_player]

        # Le joueur peut jouer sans passer son tour
        if checkPossibilityAction(self, player.hand):
            return (False, "MOVE_POSSIBLE")

        # Le joueur n'a pas encore essayé de piocher
        if not player.draw:
            return (False, "DRAW_POSSIBLE")

        player.draw = False  # Réinitialiser le flag de pioche du joueur
        self.next_player()  # Passer la main au joueur suivant
        return (True, "OK")

    def uno(self, pseudo):
        """ Traiter l'action Crier UNO

        Parameters:
            pseudo (string): Pseudo du joueur qui a effectué l'action

        Returns:
            (bool): Succès de l'action du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        # La partie n'a pas encore commencé
        if not self.started:
            return (False, "NOT_STARTED")
        
        for player in self.players:
            if player.pseudo == pseudo:
                uno_player = player

        if uno_player.uno :
            return (False, "ALREADY_UNO")

        if len(uno_player.hand) != 1: # Le joueur a plus d'une seule carte dans sa main
            return (False, "NO_UNO")
        
        uno_player.uno = True
        return (True, "OK")
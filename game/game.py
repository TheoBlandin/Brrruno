from game.deck import Deck
from game.player import Player
from utils.colors import COLORS
from utils.rules import checkPossibilityAction, checkAction
import asyncio

FORBIDDEN_START = [
    f"joker_couleurs",
    f"joker_+4",
    f"rouge_passeTonTour",
    f"vert_passeTonTour",
    f"bleu_passeTonTour",
    f"jaune_passeTonTour",
    f"rouge_changeDeSens",
    f"vert_changeDeSens",
    f"bleu_changeDeSens",
    f"jaune_changeDeSens",
    f"rouge_+2",
    f"vert_+2",
    f"bleu_+2",
    f"jaune_+2",
]
TURN_TIMEOUT = 30

class Game:
    """Partie de jeu de Uno

    Attributes:
        deck (Deck): Paquet de carte
        started (bool): Statut de la partie
        players (Player[]): Liste des joueurs membres de la partie
        current_player (int): Indice du joueur actuel dans le tableau players
        finish_order (str[]): Pseudo des gagnants, par ordre du plus rapide
        current_card (str): Carte sur laquelle le joueur actuel doit jouer
        direction (int): Sens du jeu, avec 1 pour le sens classique et -1 pour le sens inverse
        turn_timer (asyncio.Task | None): Temps écoulé entre deux actions d'un joueur
    """

    def __init__(self):
        """Initialise la partie"""

        self.deck = Deck()
        self.started = False

        self.players = []
        self.current_player = 0
        self.finish_order = []

        self.current_card = None

        self.direction = 1

        self.turn_timer = None

    async def start_timer(self, bot, channel):
        try:
            await asyncio.sleep(TURN_TIMEOUT)

            player = self.players[self.current_player]

            await bot.send(
                f"PRIVMSG {channel} :\x02On dirait que {player.pseudo} s'est endormi-e...\x02"
            )

            await asyncio.sleep(TURN_TIMEOUT)

            await bot.send(
                f"PRIVMSG {channel} :\x02Tant pis pour toi {player.pseudo}. Pour ta peine, tu vas piocher une carte. \x02"
            )

            new_card = self.deck.draw()
            player.add_card(new_card)

            new_card = COLORS[new_card.split("_")[0]] + " " + new_card

            await bot.send(
                f"NOTICE {player.pseudo} :\x02Tu as pioché la carte {new_card}.\x02"
            )

            self.next_player()  # Passer au joueur suivant
            self.turn_timer = asyncio.create_task(
                self.start_timer(bot, channel)
            )  # Démarrer un nouveau timer

            new_player = self.players[self.current_player]
            # Cas où le joueur précédent a passé son tour après un joker
            if self.current_card.split("_")[1] == "undefined":
                color = self.current_card.split("_")[0]
                color = COLORS[color] + " " + color

                await bot.send(
                    f"PRIVMSG {channel} :\x02{player.pseudo} n'as pas pu jouer à temps. C'est à {new_player.pseudo} de jouer. La couleur est {color}\x02"
                )
            else:
                current_card = (
                    COLORS[self.current_card.split("_")[0]] + " " + self.current_card
                )

                await bot.send(
                    f"PRIVMSG {channel} :\x02{player.pseudo} n'as pas pu jouer à temps. C'est à {new_player.pseudo} de jouer. La carte est {current_card}\x02"
                )

            if (
                len(new_player.hand) == 1 and not new_player.uno
            ):  # Le joueur n'a pas dit UNO
                cards = []
                for _ in range(2):  # Piocher 2 cartes
                    new_card = self.deck.draw()
                    new_player.add_card(new_card)

                    cards.append(COLORS[new_card.split("_")[0]] + " " + new_card)
                drawed_string = ", ".join(cards)

                await bot.send(
                    f"PRIVMSG {channel} :\x02{new_player.pseudo} n'a pas dit UNO ! Tu pioche 2 cartes.\x02"
                )
                await bot.send(
                    f"NOTICE {new_player.pseudo} :\x02Tu as pioché les cartes suivantes : {drawed_string}.\x02"
                )

            nb_card = len(new_player.hand)
            cards = []
            for i in range(nb_card):
                card = new_player.hand[i]
                # Ajouter le carré de couleur correspondant
                card = COLORS[card.split("_")[0]] + " " + card
                cards.append(card)
            hand_string = ", ".join(cards)

            await bot.send(
                f"NOTICE {new_player.pseudo} :\x02Voici ta main : {hand_string}\x02"
            )
        except asyncio.CancelledError:
            return

    def restart_timer(self, bot, channel):
        if self.turn_timer is not None and not self.turn_timer.done():
            self.turn_timer.cancel()

        self.turn_timer = asyncio.create_task(self.start_timer(bot, channel))

    def add_player(self, pseudo):
        """Ajouter un joueur dans la partie

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

    def remove_player(self, pseudo):
        """Retirer un joueur de la partie

        Parameters :
            pseudo (str): Pseudo du joueur à retirer

        Returns:
            (bool): Succès du retrait du joueur
            (str): Message justificatif du succès ou de l'échec
        """
        for player in self.players:
            if player.pseudo == pseudo:
                self.players.remove(player)
                return (True, "OK")

        return (False, "NOT_IN")

    def see_players(self):
        """Voir la liste des joueurs présents dans la partie

        Returns:
            (str[]): Liste d'objet Player
        """

        return self.players

    def start_game(self, bot, channel):
        """Lancer la partie

        Returns:
            (bool): Succès du lancement de la partie
            (str): Message justificatif du succès ou de l'échec
        """

        if self.started:  # Partie déjà en cours
            return (False, "ALREADY_STARTED")

        if len(self.players) < 2:  # Pas assez de joueurs
            return (False, "NOT_ENOUGH")

        self.restart_timer(bot, channel)  # Démarrer un nouveau timer
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
        """Traiter l'action Jouer une carte

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
        card_color, card_symbol = card.split("_")
        if card_symbol == "changeDeSens":
            self.direction *= -1
            await bot.send(f"PRIVMSG {channel} :\x02Attention, la roue tourne !\x02")
        elif card_symbol == "passeTonTour":
            self.next_player()  # Passer directement le tour du joueur suivant
            await bot.send(
                f"PRIVMSG {channel} :\x02Désolé {self.players[self.current_player].pseudo}, mais tu ne joueras pas cette fois-ci.\x02"
            )
        elif card_color.startswith("joker"):
            if card_symbol == "+4":  # Carte joker +4
                self.next_player()  # Joueur qui va piocher
                new_player = self.players[self.current_player]

                cards = []
                for _ in range(4):  # Piocher 4 cartes
                    new_card = self.deck.draw()
                    new_player.add_card(new_card)

                    cards.append(COLORS[new_card.split("_")[0]] + " " + new_card)

                drawed_string = ", ".join(cards)

                await bot.send(
                    f"PRIVMSG {channel} :\x02Ouille, ça fait mal ! {new_player.pseudo} pioche 4 cartes.\x02"
                )

                await bot.send(
                    f"NOTICE {new_player.pseudo} :\x02Tu as pioché les cartes suivantes : {drawed_string}.\x02"
                )

            # Joker +4 et Joker simple
            new_color = COLORS[parts[2]] + ' ' + parts[2]

            self.next_player()  # Joueur qui va jouer
            new_player = self.players[self.current_player]
            new_player.draw = False  # Réinitialiser le flag de pioche du joueur
            # Construction d'une fausse carte pour la couleur et tour suivant
            self.current_card = parts[2] + "_undefined"

            await bot.send(f"PRIVMSG {channel} :\x02La nouvelle couleur est {new_color}. C'est à {new_player.pseudo} de jouer.\x02")

            if len(new_player.hand) == 1 and not new_player.uno: # Le joueur n'a pas dit UNO
                cards = []
                for _ in range(2):  # Piocher 2 cartes
                    new_card = self.deck.draw()
                    new_player.add_card(new_card)

                    cards.append(COLORS[new_card.split('_')[0]] + ' ' + new_card)
                drawed_string = ", ".join(cards)

                await bot.send(f"\x02PRIVMSG {channel} :{new_player.pseudo} n'a pas dit UNO ! Tu pioche 2 cartes.\x02")
                await bot.send(f"\x02NOTICE {new_player.pseudo} :Tu as pioché les cartes suivantes : {drawed_string}.\x02")

            nb_card = len(new_player.hand)
            cards = []
            for i in range(nb_card):
                card = new_player.hand[i]
                # Ajouter le carré de couleur correspondant
                card = COLORS[card.split('_')[0]] + ' ' + card
                cards.append(card)
            hand_string = ", ".join(cards)

            await bot.send(f"NOTICE {new_player.pseudo} :\x02Voici ta main : {hand_string}\x02")

            # Tour suivant
            self.restart_timer(bot, channel)
            return (True, "COULEUR")
            
        elif card_symbol == "+2":
            # On passe le tour du joueur qui va piocher
            self.next_player()
            new_player = self.players[self.current_player]

            cards = []
            for _ in range(2):  # Piocher 2 cartes
                new_card = self.deck.draw()
                new_player.add_card(new_card)

                cards.append(COLORS[new_card.split("_")[0]] + " " + new_card)

            drawed_string = ", ".join(cards)

            await bot.send(
                f"PRIVMSG {channel} :\x02Ouille, ça fait mal ! {new_player.pseudo} pioche 2 cartes.\x02"
            )
            await bot.send(
                f"NOTICE {new_player.pseudo} :\x02Tu as pioché les cartes suivantes :  {drawed_string}.\x02"
            )

        if len(player.hand) == 0:  # Le joueur n'a plus de carte en main
            await bot.send(
                f"PRIVMSG {channel} :\x02{player.pseudo} a terminé, félicitations !\x02"
            )
            self.current_player = (self.current_player + (-self.direction)) % len(self.players) # Le joueur "en cours" devient celui d'avant, pour pouvoir passer la main sans sauter un tour
            self.remove_player(player.pseudo)
            # Ajouter le joueur à la liste des gagnants
            self.finish_order.append(player.pseudo)
            if len(self.players) == 1:  # Il n'y a plus qu'un seul joueur dans la partie
                self.started = False  # Fin de la partie
                return (False, "END")

        # Tour suivant
        player.draw = False  # Réinitialiser le flag de pioche du joueur
        self.current_card = card  # Mettre à jour la carte du haut du paquet
        self.next_player()  # Passer la main au joueur suivant
        self.restart_timer(bot, channel)
        return (check, "OK")

    def draw_card(self, bot, pseudo, channel):
        """Gérer l'action piocher d'un joueur

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
        player.uno = False  # Réinitialiser Uno

        if len(self.deck.cards) == 0:  # pioche vide
            self.deck.refill()  # Recréer une pioche avec les cartes non en jeu

        self.restart_timer(bot, channel)

        return (True, "OK")

    def next_player(self):
        """Passer au joueur suivant"""

        self.current_player = (self.current_player + self.direction) % len(self.players)

    def pass_turn(self, bot, pseudo, channel):
        """Traiter l'action Passer son tour

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
        self.restart_timer(bot, channel)  # Démarrer un nouveau timer
        return (True, "OK")

    def uno(self, pseudo):
        """Traiter l'action Crier UNO

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

        if uno_player.uno:
            return (False, "ALREADY_UNO")

        if len(uno_player.hand) != 1:  # Le joueur a plus d'une seule carte dans sa main
            return (False, "NO_UNO")

        uno_player.uno = True
        return (True, "OK")

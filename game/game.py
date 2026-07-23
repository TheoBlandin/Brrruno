# Objects
import random

from game.deck import Deck
from game.player import Player

# Data
from utils.colors import COLORS

# Functions
from utils.rules import checkPossibilityAction, checkAction, checkUno
from utils.utils import showHand

# Libraries
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
START_TIMEOUT = 120


class Game:
    """Partie de jeu de Uno

    Attributes:
        deck (Deck): Paquet de carte
        bot (IRCClient): Bot de jeu connecté à l'IRC
        channel (str): Salon dans lequel la partie se déroule
        started (bool): Statut de la partie
        players (Player[]): Liste des joueurs membres de la partie
        current_player (Player | None): Pseudo du joueur dont c'est le tour
        finish_order (str[]): Pseudo des gagnants, par ordre du plus rapide
        current_card (str): Carte sur laquelle le joueur actuel doit jouer
        direction (int): Sens du jeu, avec 1 pour le sens classique et -1 pour le sens inverse
        waiting_for_color (bool): Flag d'attente d'une couleur après une carte Joker
        starting_timer (asyncio.Task | None): Timer avant lequel la partie va commencer
        turn_timer (asyncio.Task | None): Gestion du temps pour le tour d'un joueur, limité à 60sec
    """

    def __init__(self):
        """Initialise la partie"""

        self.deck = Deck()
        self.bot = None
        self.channel = None
        self.started = False

        self.players = []
        self.current_player = None
        self.finish_order = []

        self.current_card = None
        self.direction = 1

        self.waiting_for_color = False

        self.starting_timer = None  # Timer pour lancer la partie
        self.turn_timer = None  # Timer pour un tour

    def build(self, bot, channel):
        """Initialiser les données relatives à l'IRC"""

        self.bot = bot
        self.channel = channel

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

        if any(player.pseudo == pseudo for player in self.players):  # Joueur déjà enregistré
            return (False, "ALREADY_IN")

        self.players.append(Player(pseudo))

        if len(self.players) == 2:
            self.restart_starting_timer()
        elif len(self.players) < 2:
            self.starting_timer = None

        return (True, "OK")

    def remove_player(self, pseudo):
        """Retirer un joueur de la partie

        Parameters :
            bot (IRCClient): Bot de jeu connecté à l'IRC
            pseudo (str): Pseudo du joueur à retirer
            channel (str): Salon dans lequel la partie se déroule

        Returns:
            (bool): Succès du retrait du joueur
            (str): Message justificatif du succès ou de l'échec
        """

        for player in self.players:
            if player.pseudo == pseudo:
                if self.started:
                    if (
                        self.current_player.pseudo == pseudo
                    ):  # La partie est en cours, et c'est le joueur qui a la main qui quitte la partie
                        self.next_turn()
                        self.players.remove(player)
                        return (True, "NEXT_PLAYER")
                    self.players.remove(player)
                    if (
                        len(self.players) == 1
                    ):  # Il n'y a plus qu'un seul joueur dans la partie
                        self.started = False  # Fin de la partie
                        return (True, "END")
                self.players.remove(player)

                if len(self.players) < 2:
                    self.starting_timer = (
                        None  # Annuler le timer en cours pour le lancement de la partie
                    )
                return (True, "OK")

        return (False, "NOT_IN")

    def next_player(self):
        """Passer au joueur suivant"""

        old_index = self.players.index(self.current_player)
        new_index = (old_index + self.direction) % len(self.players)
        self.current_player = self.players[new_index]

    def next_turn(self):
        """Démarrer un nouveau tour"""
        self.current_player.draw = False  # Réinitialiser le flag de pioche du joueur qui vient de terminer son tour

        self.next_player()  # Passer au joueur suivant

        self.restart_turn_timer()  # Démarrer un nouveau timer

    async def start_starting_timer(self):
        """Lancer le timer de lancement d'une partie"""

        try:
            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02La partie va commencer dans 2 minutes. Tapez !joueurs pour voir la liste des joueurs, et !go pour rejoindre la partie.\x02"
            )

            await asyncio.sleep(START_TIMEOUT - 15)

            # Dernière chance
            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02Attention, il ne reste plus que 15 secondes pour rejoindre la partie ! Tapez !joueurs pour voir la liste des joueurs, et !go pour rejoindre la partie.\x02"
            )

            await asyncio.sleep(15)
            await self.start_game()  # Lancer la partie

        except asyncio.CancelledError:
            return

    def restart_starting_timer(self):
        """Réinitialiser le timer de lancement d'une partie"""

        if self.starting_timer is not None and not self.starting_timer.done():
            self.starting_timer.cancel()

        self.starting_timer = asyncio.create_task(self.start_starting_timer())

    async def start_turn_timer(self):
        """Lancer le timer d'un tour"""

        try:
            # Premier délai
            await asyncio.sleep(TURN_TIMEOUT)

            # Rappel
            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02On dirait que {self.current_player.pseudo} s'est endormi-e...\x02"
            )

            # Deuxième délai
            await asyncio.sleep(TURN_TIMEOUT)

            # Passer le tour du joueur afk et le faire piocher une carte
            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02Tant pis pour toi {self.current_player.pseudo}. Pour ta peine, tu vas piocher une carte. \x02"
            )

            new_card = self.deck.draw()
            self.current_player.add_card(new_card)
            new_card = COLORS[new_card.split("_")[0]] + " " + new_card
            await self.bot.send(
                f"NOTICE {self.current_player.pseudo} :\x02Tu as pioché la carte {new_card}.\x02"
            )

            old_player = self.current_player

            if self.waiting_for_color: # Choix d'une couleur en attente
                colors = ["rouge_undefined", "vert_undefined", "bleu_undefined", "jaune_undefined"]
                self.current_card = colors[random.randint(0, 3)]
                self.waiting_for_color = False

            self.next_turn()

            # Cas où le joueur précédent a passé son tour après un joker
            if self.current_card.split("_")[1] == "undefined":
                color = self.current_card.split("_")[0]
                color = COLORS[color] + " " + color

                await self.bot.send(
                    f"PRIVMSG {self.channel} :\x02{old_player.pseudo} n'a pas pu jouer à temps. C'est à {self.current_player.pseudo} de jouer. La couleur est {color}\x02"
                )
            else:
                current_card = (
                    COLORS[self.current_card.split("_")[0]] + " " + self.current_card
                )

                await self.bot.send(
                    f"PRIVMSG {self.channel} :\x02{old_player.pseudo} n'a pas pu jouer à temps. C'est à {self.current_player.pseudo} de jouer. La carte est {current_card}\x02"
                )

            await checkUno(
                self, self.current_player
            )  # Vérifier le joueur devait dire Uno, et s'il l'a fait, sinon le faire piocher

            await showHand(
                self, self.current_player
            )  # Donner sa main au joueur dont c'est le tour
        except asyncio.CancelledError:
            return

    def restart_turn_timer(self):
        """Réinitialiser le timer"""

        if self.turn_timer is not None and not self.turn_timer.done():
            self.turn_timer.cancel()

        self.turn_timer = asyncio.create_task(self.start_turn_timer())

    async def start_game(self):
        """Lancer la partie

        Parameters :
            bot (IRCClient): Bot de jeu connecté à l'IRC
            channel (str): Salon dans lequel la partie se déroule
        """

        self.starting_timer = None  # Annuler le timer
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

        self.restart_turn_timer()  # Démarrer un nouveau timer
        self.current_player = self.players[0]  # Premier joueur à jouer

        await self.bot.send(f"PRIVMSG {self.channel} :\x02La partie va commencer !\x02")

        for p in self.players:
            await showHand(self, p)  # Donner sa main au joueur

        current_card = self.current_card
        current_card = COLORS[current_card.split("_")[0]] + " " + current_card

        await self.bot.send(
            f"PRIVMSG {self.channel} :\x02Les cartes ont été distribuées. Si vous ne voyez pas vos cartes, regardez dans le salon #TGPIRC.\x02"
        )
        await self.bot.send(
            f"PRIVMSG {self.channel} :\x02La première carte est : {current_card}. C'est à {self.current_player.pseudo} de jouer.\x02"
        )

    async def play(self, pseudo, msg):
        """Traiter l'action Jouer une carte

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
        if self.current_player.pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        player = self.current_player
        parts = msg.split()
        # Aucune carte sélectionnée
        if len(parts) < 2:
            return (False, "NO_CARD")

        # Le joueur ne possède pas cette carte dans sa main
        card = parts[1]
        lower_hand = [
            card.lower() for card in player.hand
        ]  # Vérification insensible à la casse
        if card.lower() not in lower_hand:
            return (False, "NOT_IN_HAND")

        card = player.hand[
            lower_hand.index(card)
        ]  # Retrouver le bon formattage de la carte, sensible à la casse

        # Vérifier la possibilité d'une action en fonction des règles
        check = checkAction(self, card)
        if not check:
            return (check, "INVALID")  # Cette action n'est pas possible

        card_color, card_symbol = card.split("_")
        player.play_card(card)  # Retirer la carte de la main du joueur

        # Gestion des cartes spéciales
        if card_symbol == "changeDeSens":
            self.direction *= -1
            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02Attention, la roue tourne !\x02"
            )
        elif card_symbol == "passeTonTour":
            self.next_turn()  # Passer directement le tour du joueur suivant
            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02Désolé {player.pseudo}, mais tu ne joueras pas cette fois-ci.\x02"
            )
        elif card_color == "joker":        
            if card_symbol == "+4":  # Carte joker +4
                # Joueur qui va piocher
                old_index = self.players.index(self.current_player)
                new_index = (old_index + self.direction) % len(self.players)
                next_player = self.players[new_index]

                cards = []
                for _ in range(4):  # Piocher 4 cartes
                    new_card = self.deck.draw()
                    next_player.add_card(new_card)

                    cards.append(COLORS[new_card.split("_")[0]] + " " + new_card)

                drawed_string = ", ".join(cards)

                await self.bot.send(
                    f"PRIVMSG {self.channel} :\x02Ouille, ça fait mal ! {next_player.pseudo} pioche 4 cartes.\x02"
                )
                await self.bot.send(
                    f"NOTICE {next_player.pseudo} :\x02Tu as pioché les cartes suivantes : {drawed_string}.\x02"
                )

            self.restart_turn_timer()  # Démarrer un nouveau timer
            self.waiting_for_color = True # Attendre que le joueur ai choisit une couleur

            return (True, "WAITING_COLOR")

        elif card_symbol == "+2":
            # On passe le tour du joueur qui va piocher
            self.next_turn()

            cards = []
            for _ in range(2):  # Piocher 2 cartes
                new_card = self.deck.draw()
                self.current_player.add_card(new_card)

                cards.append(COLORS[new_card.split("_")[0]] + " " + new_card)

            drawed_string = ", ".join(cards)

            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02Ouille, ça fait mal ! {self.current_player.pseudo} pioche 2 cartes.\x02"
            )
            await self.bot.send(
                f"NOTICE {self.current_player.pseudo} :\x02Tu as pioché les cartes suivantes :  {drawed_string}.\x02"
            )

        if len(self.current_player.hand) == 0:  # Le joueur n'a plus de carte en main
            await self.bot.send(
                f"PRIVMSG {self.channel} :\x02{self.current_player.pseudo} a terminé, félicitations !\x02"
            )
            self.remove_player(self.current_player.pseudo)

            # Ajouter le joueur à la liste des gagnants
            self.finish_order.append(self.current_player.pseudo)
            if len(self.players) == 1:  # Il n'y a plus qu'un seul joueur dans la partie
                self.started = False  # Fin de la partie
                self.players = []  # Réinitialisation du tableau des joueurs
                self.turn_time = None  # Annulation du timer
                return (False, "END")

        self.current_card = card  # Mettre à jour la carte du haut du paquet
        self.next_turn()
        return (True, "OK")

    def draw_card(self, pseudo):
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
        if self.current_player.pseudo != pseudo:
            return (False, "NOT_YOUR_TURN")

        # Le joueur a déjà pioché ce tour-ci
        if self.current_player.draw:
            return (False, "ALREADY_DRAW")

        # Le joueur peut jouer sans piocher
        if checkPossibilityAction(self, self.current_player.hand):
            return (False, "MOVE_POSSIBLE")

        new_card = self.deck.draw()
        self.current_player.add_card(new_card)
        self.current_player.draw = True
        self.current_player.uno = False  # Réinitialiser Uno

        if len(self.deck.cards) == 0:  # Pioche vide
            self.deck.refill()  # Recréer une pioche avec les cartes non en jeu

        # Le joueur peut jouer
        if checkAction(self, new_card):
            self.restart_turn_timer()
            return (True, "OK")

        # Le joueur ne peut pas jouer, on passe son tour
        return (True, "PASS")

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

    def choose_color(self, pseudo, color):
        if not self.started:
            return (False, "NOT_STARTED")

        if pseudo != self.current_player.pseudo:
            return (False, "NOT_YOUR_TURN")

        if not self.waiting_for_color:
            return (False, "NOT_ASKED")

        chosen_color = color.replace('!', '')
        self.current_card = chosen_color + "_undefined" # Construction d'une fausse carte pour la couleur
        self.waiting_for_color = False
        self.next_turn()
        return (True, "OK")

from uno.deck import Deck
from uno.player import Player
from utils.colors import COLORS
from utils.rules import checkPossibilityAction, checkAction

FORBIDDEN_START = [f"joker_couleurs", f"joker_+4", f"rouge_passeTonTour", f"vert_passeTonTour", f"bleu_passeTonTour", f"jaune_passeTonTour",
                   f"rouge_changeDeSens", f"vert_changeDeSens", f"bleu_changeDeSens", f"jaune_changeDeSens", f"rouge_+2", f"vert_+2", f"bleu_+2", f"jaune_+2"]


class Uno:
    def __init__(self):
        self.players = []
        self.started = False

        self.deck = Deck()

        self.current_card = None
        self.current_player = 0

        self.direction = 1

        self.ask_color = False

    def add_player(self, pseudo):
        if self.started:  # Partie déjà en cours
            return (False, "ALREADY_STARTED")

        if pseudo in self.players:  # Joueur déjà enregistré
            return (False, "ALREADY_IN")

        self.players.append(Player(pseudo))
        return (True, "OK")

    def remove_player(self, pseudo):
        if self.started:
            return (False, "ALREADY_STARTED")

        for player in self.players:
            if player.pseudo == pseudo:
                self.players.remove(player)
                return (True, "OK")

        return (False, "NOT_IN")

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

    async def play(self, bot, pseudo, channel, msg):
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

        # Le joueur ne possède pas sa carte dans sa main
        player = self.players[self.current_player]
        card = parts[1]
        if card not in player.hand:
            return (False, "NOT_IN_HAND")

        # Vérifier la validité du coup
        check = checkAction(self, card)
        if not check:
            return (check, "INVALID")

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

                for _ in range(4):  # Piocher 4 cartes
                    next_player.add_card(self.deck.draw())

                await bot.send(f"PRIVMSG {channel} :Ouille, ça fait mal ! {next_player.pseudo} pioche 4 cartes.")

                nb_card = len(next_player.hand)

                hand_string = ''
                drawed_string = ''
                for i in range(nb_card):
                    card = next_player.hand[i]
                    # Ajouter le carré de couleur correspondant
                    card = COLORS[card.split('_')[0]] + ' ' + card

                    if i >= nb_card - 4:  # 4 dernières cartes de la main
                        drawed_string += card + ', '
                        if i + 1 == nb_card:  # Dernière carte de la main
                            hand_string += card
                            drawed_string += card
                    else:
                        hand_string += card + ', '

                await bot.send(f"NOTICE {next_player.pseudo} :Tu as pioché les cartes {drawed_string}. Voici ta main : {hand_string}")

            await self.asking_color(bot, channel)
            return (False, "WAIT_COLOR")

        # Tour suivant
        player.draw = False  # Réinitialiser le flag de pioche du joueur
        self.current_card = card  # Mettre à jour la carte du haut du paquet
        self.next_player()  # Passer la main au joueur suivant
        return (check, "OK")

    def draw_card(self, pseudo):
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
        return (True, "OK")

    def next_player(self):
        self.current_player = (self.current_player +
                               self.direction) % len(self.players)

    async def asking_color(self, bot, channel):
        await bot.send(f"PRIVMSG {channel} :Quelle nouvelle couleur choisis-tu ?")
        self.ask_color = True

    def choose_color(self, pseudo, msg):
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

class Player:
    """ Joueur membre de la partie

    Attributes:
        pseudo (str): Pseudo du joueur
        hand (str[]): Cartes composants la main du joueur
        draw (bool): Flag pour savoir si un joueur a déjà pioché
        uno (bool): Flag pour savoir si un joueur a crié UNO
    """

    def __init__(self, pseudo):
        """ Initialise un objet Player

        Parameters:
            pseudo (str): Pseudo du joueur
        """

        self.pseudo = pseudo
        self.hand = []
        self.draw = False
        self.uno = False

    def add_card(self, card):
        """ Ajouter une carte dans la main du joueur

        Parameters:
            card (str): Carte à ajouter
        """

        self.hand.append(card)

    def play_card(self, card):
        """ Retirer une carte de la main du joueur

        Parameters:
            card (str): Carte à retirer
        """

        self.hand.remove(card)

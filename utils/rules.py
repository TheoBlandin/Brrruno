# Vérifier que le coup est possible
def checkAction(game, player_card):
    """ Vérifie si le coup est possible.

    Parameters:
        game (Uno): Jeu en cours
        player_card (string): Carte du joueur

    Returns:
        boolean: True si le coup est possible, False sinon
    """

    current_color, current_symbol = game.current_card.split('_')
    player_color, player_symbol = player_card.split('_')

    # Carte joker OU même couleur OU même symbole
    if player_color == "joker" or current_color == player_color or current_symbol == player_symbol:
        return True

    return False


def checkPossibilityAction(game, player_hand):
    """ Vérifie si un coup est possible dans la main du joueur.

    Parameters:
        game (Uno): Jeu en cours
        player_hand (str[]): Main du joueur

    Returns:
        boolean: True si un coup est possible, False sinon
    """

    flag = False  # Coup possible
    i = 0
    while not flag and i < len(player_hand):
        flag = checkAction(game, player_hand[i])
        i += 1

    return flag

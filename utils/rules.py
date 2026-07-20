# Vérifier que le coup est possible
from utils.colors import COLORS

def checkAction(game, player_card):
    """ Vérifie si le coup est possible.

    Parameters:
        game (Game): Jeu en cours
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
        game (Game): Jeu en cours
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

async def checkUno(game, player):
    """ Vérifier si le joueur devait dire Uno, et le faire piocher s'il ne l'a pas dit

    Parameters:
        game (Game): Partie de Uno
        player (Player): Objet Player dont c'est le tour
    """

    if len(player.hand) == 1 and not player.uno: # Le joueur n'a pas dit UNO
        cards = []
        for _ in range(2):  # Piocher 2 cartes
            new_card = game.deck.draw()
            player.add_card(new_card)

            cards.append(COLORS[new_card.split('_')[0]] + ' ' + new_card)
        drawed_string = ", ".join(cards)

        await game.bot.send(f"PRIVMSG {game.channel} :\x02{player.pseudo} n'a pas dit UNO ! Tu pioches 2 cartes.\x02")
        await game.bot.send(f"NOTICE {player.pseudo} :\x02Tu as pioché les cartes suivantes : {drawed_string}.\x02")
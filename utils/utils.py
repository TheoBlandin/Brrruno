# Data
from utils.colors import COLORS

async def showHand(game, player):
    """ Donner sa main en Notice au joueur player

    Parameters:
        game (Game): Jeu en cours
        player (Player): Joueur qui va recevoir sa main
    """

    nb_card = len(player.hand)
    cards = []
    for i in range(nb_card):
        card = player.hand[i]
        # Formater la carte
        card = COLORS[card.split('_')[0]] + ' ' + card
        cards.append(card)
    hand_string = ", ".join(cards)

    await game.bot.send(f"NOTICE {player.pseudo} :\x02Voici ta main : {hand_string}\x02")
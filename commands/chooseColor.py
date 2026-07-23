# Data
from utils.colors import COLORS

# Functions
from utils.rules import checkUno
from utils.utils import showHand


async def chooseColor(game, pseudo, msg):
    """ Traiter la réponse du bot à l'action Choisir une couleur

    Parameters:
        game (Game): Partie de Uno
        pseudo (str): Pseudo du joueur ayant effectué l'action
        msg (string): Message du joueur composant son action
    """

    success, message = game.choose_color(pseudo, msg)

    if success:
        color = game.current_card.split('_')[0]
        color = COLORS[color] + ' ' + color

        await game.bot.send(f"PRIVMSG {game.channel} :\x02La nouvelle couleur est {color}. C'est à {game.current_player.pseudo} de jouer.\x02")

        await checkUno(
            game, game.current_player
        )  # Vérifier le joueur devait dire Uno, et s'il l'a fait, sinon le faire piocher

        await showHand(
            game, game.current_player
        )  # Donner sa main au joueur dont c'est le tour
    else:
        match message:
            case "NOT_STARTED":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02La partie n'a pas encore commencé.\x02")
            case "NOT_YOUR_TURN":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02Ce n'est pas à ton tour de jouer.\x02")
            case "NOT_ASKED":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02Ce n'est pas le moment de choisir une couleur.\x02")

# Data
from utils.colors import COLORS

# Functions
from utils.rules import checkUno
from utils.utils import showHand


async def passTurn(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Passer son tour

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur qui a passé son tour
        channel (str): Salon dans lequel la partie se déroule
    """

    success, message = game.pass_turn(pseudo)

    if success:
        # Cas où le joueur précédent a passé son tour après un joker
        if game.current_card.split('_')[1] == 'undefined':
            color = game.current_card.split('_')[0]
            color = COLORS[color] + ' ' + color

            await bot.send(f"PRIVMSG {channel} :\x02{pseudo} a passé son tour. C'est à {game.current_player.pseudo} de jouer. La couleur est {color}.\x02")
        else:
            current_card = COLORS[game.current_card.split(
                '_')[0]] + ' ' + game.current_card

            await bot.send(f"PRIVMSG {channel} :\x02{pseudo} a passé son tour. C'est à {game.current_player.pseudo} de jouer. La carte est {current_card}.\x02")

        await checkUno(game, game.current_player) # Vérifier le joueur devait dire Uno, et s'il l'a fait, sinon le faire piocher

        await showHand(game, game.current_player) # Donner sa main au joueur dont c'est le tour
    else:
        match message:
            case "NOT_STARTED":
                await bot.send(f"PRIVMSG {channel} :\x02La partie n'a pas encore commencé.\x02")
            case "NOT_YOUR_TURN":
                await bot.send(f"PRIVMSG {channel} :\x02Ce n'est pas à ton tour de jouer.\x02")
            case "MOVE_POSSIBLE":
                await bot.send(f"PRIVMSG {channel} :\x02Tu peux jouer sans passer ton tour.\x02")
            case "DRAW_POSSIBLE":
                await bot.send(f"PRIVMSG {channel} :\x02Essaye de piocher une carte avant de passer ton tour.\x02")

# Data
from utils.colors import COLORS

# Functions
from utils.utils import showHand

async def draw(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Piocher une carte

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur qui a pioché une carte
        channel (str): Salon dans lequel la partie se déroule
    """

    success, message = game.draw_card(pseudo)

    if success:
        await bot.send(f"PRIVMSG {channel} :\x02{game.current_player.pseudo} a pioché une carte ! Pourra-t-iel jouer cette fois-ci ?\x02")
 
        drawed_card = game.current_player.hand[-1]
        drawed_card = COLORS[drawed_card.split('_')[0]] + ' ' + drawed_card
        await bot.send(f"NOTICE {game.current_player.pseudo} :\x02Tu as pioché la carte {drawed_card}.\x02")

        await showHand(game, game.current_player) # Donner sa main au joueur 
    else:
        match message:
            case "NOT_STARTED":
                await bot.send(f"PRIVMSG {channel} :\x02La partie n'a pas encore commencé.\x02")
            case "NOT_YOUR_TURN":
                await bot.send(f"PRIVMSG {channel} :\x02Ce n'est pas à ton tour de jouer.\x02")
            case "ALREADY_DRAW":
                await bot.send(f"PRIVMSG {channel} :\x02Tu as déjà pioché.\x02")
            case "MOVE_POSSIBLE":
                await bot.send(f"PRIVMSG {channel} :\x02Tu peux déjà jouer sans piocher de nouvelle carte.\x02")

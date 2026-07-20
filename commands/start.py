# Data
from utils.colors import COLORS

# Functions
from utils.utils import showHand

async def startGame(game, bot, channel):
    """ Traiter la réponse du bot à l'action Lancer la partie

    Parameters:
        game (Game): Partie de Uno 
        bot (IRCClient): Bot de jeu connecté à l'IRC
        channel (str): Salon dans lequel la partie se déroule
    """

    success, message = game.start_game(bot, channel)

    if success:
        await bot.send(f"PRIVMSG {channel} :\x02La partie va commencer !\x02")

        for p in game.players:
            await showHand(game, p) # Donner sa main au joueur 
    
        current_card = game.current_card
        current_card = COLORS[current_card.split('_')[0]] + ' ' + current_card

        await bot.send(f"PRIVMSG {channel} :\x02Les cartes ont été distribuées. Si vous ne voyez pas vos cartes, regardez dans le salon #TGPIRC.\x02")
        await bot.send(f"PRIVMSG {channel} :\x02La première carte est : {current_card}. C'est à {game.current_player.pseudo} de jouer.\x02")

    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :\x02La partie est déjà en cours.\x02")
            case "NOT_ENOUGH":
                await bot.send(f"PRIVMSG {channel} :\x02Il faut deux joueurs minimum pour lancer une partie. Taper !join pour rejoindre la partie.\x02")

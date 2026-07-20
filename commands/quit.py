# Data
from utils.colors import COLORS

# Functions
from utils.rules import checkUno
from utils.utils import showHand
from utils.winners import WINNERS

async def quitGame(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Quitter la partie

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.remove_player(pseudo)

    if success:
        match message:
            case "OK":
                await bot.send(f"PRIVMSG {channel} :\x02{pseudo} a quitté la partie.\x02")
            case "NEXT_PLAYER":
                await bot.send(f"PRIVMSG {channel} :\x02On dirait que {pseudo} a fuit face à l'adversité et a quitté la partie...\x02")

                # Cas où le joueur précédent est parti après un joker
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
            case "END":
                winners = []
                for i in range(len(game.finish_order)):
                    winner = WINNERS[i] if i < 3 else '' + game.finish_order[i]
                    winners.append(winner)
                winner_string = ", ".join(winners)

                await bot.send(f"PRIVMSG {channel} :\x02La partie est terminée, voici le classement : {winner_string}\x02")
                await bot.send(f"PRIVMSG {channel} :\x02Prêts pour une nouvelle partie ? Tapez !join pour rejoindre la partie !\x02")
    else:
        match message:
            case "NOT_IN":
                await bot.send(f"PRIVMSG {channel} :\x02Tu n'es pas enregistré comme joueur.\x02")

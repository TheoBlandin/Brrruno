# Data
from utils.colors import COLORS
from utils.winners import WINNERS

# Functions
from utils.rules import checkUno
from utils.utils import showHand


async def play(game, pseudo, msg):
    """Traiter la réponse du bot à l'action Jouer une carte

    Parameters:
        game (Game): Partie de Uno
        pseudo (str): Pseudo du joueur qui a joué une carte
        msg (string): Message du joueur composant son action
    """

    success, message = await game.play(pseudo, msg)

    # Si une carte Joker a été joué, la gestion se fait dans l'objet Game directement
    if success:
        match message:
            case "OK":
                # Cas où le joueur précédent a joué une carte joker
                if game.current_card.split("_")[1] == "undefined":
                    color = game.current_card.split("_")[0]
                    color = COLORS[color] + " " + color

                    await game.bot.send(
                        f"PRIVMSG {game.channel} :\x02La nouvelle couleur est {color}. C'est à {game.current_player.pseudo} de jouer.\x02"
                    )
                else:
                    current_card = (
                        COLORS[game.current_card.split("_")[0]]
                        + " "
                        + game.current_card
                    )

                    await game.bot.send(
                        f"PRIVMSG {game.channel} :\x02La nouvelle carte est {current_card}. C'est à {game.current_player.pseudo} de jouer.\x02"
                    )

                await checkUno(
                    game, game.current_player
                )  # Vérifier le joueur devait dire Uno, et s'il l'a fait, sinon le faire piocher

                await showHand(
                    game, game.current_player
                )  # Donner sa main au joueur dont c'est le tour
            case "WAITING_COLOR":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02{game.current_player.pseudo} utilise une carte Joker ! Quelle couleur choisis-tu ?"
                )
    else:
        match message:
            case "NOT_STARTED":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02La partie n'a pas encore commencé.\x02"
                )
            case "NOT_YOUR_TURN":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Ce n'est pas à ton tour de jouer.\x02"
                )
            case "NO_CARD":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Tu n'as choisit aucune carte.\x02"
                )
            case "NOT_IN_HAND":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Cette carte n'est pas dans ta main.\x02"
                )
            case "INVALID":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Ce coup est invalide.\x02"
                )
            case "NO_COLOR":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Il faut donner une couleur lorsque l'on utilise une carte joker (!jouer <carte> <option> avec option rouge, vert, bleu ou jaune).\x02"
                )
            case "END":
                winners = []
                if len(game.finish_order) == 0:
                    await game.bot.send(
                        f"PRIVMSG {game.channel} :\x02La partie est terminée, personne n'a gagné.\x02"
                    )
                else:
                    for i in range(len(game.finish_order)):
                        winner = WINNERS[i] if i < 3 else "" + game.finish_order[i]
                        winners.append(winner)
                    winner_string = ", ".join(winners)

                    await game.bot.send(
                        f"PRIVMSG {game.channel} :\x02La partie est terminée, voici le classement : {winner_string}\x02"
                    )
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Prêts pour une nouvelle partie ? Tapez !go pour rejoindre la partie !\x02"
                )

# Data
from utils.colors import COLORS
from utils.rules import checkUno
from utils.utils import showHand


async def draw(game, pseudo):
    """Traiter la réponse du bot à l'action Piocher une carte

    Parameters:
        game (Game): Partie de Uno
        pseudo (str): Pseudo du joueur qui a pioché une carte
    """

    success, message = game.draw_card(pseudo)

    if success:
        drawed_card = game.current_player.hand[-1]
        drawed_card = COLORS[drawed_card.split("_")[0]] + " " + drawed_card
        await game.bot.send(
            f"NOTICE {game.current_player.pseudo} :\x02Tu as pioché la carte {drawed_card}.\x02"
        )

        match message:
            case "OK":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02{game.current_player.pseudo} a pioché une carte ! Mon petit doigt me dit que la situation va se débloquer...\x02"
                )
            case "PASS":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02{game.current_player.pseudo} a pioché une carte ! Malheureusement je crois que ça ne va pas suffire, {game.current_player.pseudo} va devoir passer son tour.\x02"
                )

                game.next_turn()

                # Cas où le joueur précédent a passé son tour après un joker
                if game.current_card.split("_")[1] == "undefined":
                    color = game.current_card.split("_")[0]
                    color = COLORS[color] + " " + color

                    await game.bot.send(
                        f"PRIVMSG {game.channel} :\x02C'est à {game.current_player.pseudo} de jouer. La couleur est {color}.\x02"
                    )
                else:
                    current_card = (
                        COLORS[game.current_card.split("_")[0]]
                        + " "
                        + game.current_card
                    )

                    await game.bot.send(
                        f"PRIVMSG {game.channel} :\x02 C'est à {game.current_player.pseudo} de jouer. La carte est {current_card}.\x02"
                    )

                await checkUno(
                    game, game.current_player
                )  # Vérifier le joueur devait dire Uno, et s'il l'a fait, sinon le faire piocher

                await showHand(
                    game, game.current_player
                )  # Donner sa main au joueur dont c'est le tour
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
            case "ALREADY_DRAW":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Tu as déjà pioché.\x02"
                )
            case "MOVE_POSSIBLE":
                await game.bot.send(
                    f"PRIVMSG {game.channel} :\x02Tu peux déjà jouer sans piocher de nouvelle carte.\x02"
                )

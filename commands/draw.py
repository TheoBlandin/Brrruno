from utils.colors import COLORS


async def draw(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Piocher une carte

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.draw_card(bot, pseudo, channel)

    if success:
        player = game.players[game.current_player]
        nb_card = len(player.hand)

        cards = []
        drawed_card = ''
        for i in range(nb_card):
            card = player.hand[i]
            # Ajouter le carré de couleur correspondant
            card = COLORS[card.split('_')[0]] + ' ' + card
            cards.append(card)
        hand_string = ", ".join(cards)
        drawed_card = cards[-1]

        await bot.send(f"PRIVMSG {channel} :\x02{player.pseudo} a pioché une carte ! Pourra-t-iel jouer cette fois-ci ?\x02")
        await bot.send(f"NOTICE {player.pseudo} :\x02Tu as pioché la carte {drawed_card}. Voici ta main : {hand_string}\x02")
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

from utils.colors import COLORS


async def passTurn(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Passer son tour

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.pass_turn(bot, pseudo, channel)

    if success:
        player = game.players[game.current_player]
        # Cas où le joueur précédent a passé son tour après un joker
        if game.current_card.split('_')[1] == 'undefined':
            color = game.current_card.split('_')[0]
            color = COLORS[color] + ' ' + color

            await bot.send(f"PRIVMSG {channel} :\x02{pseudo} a passé son tour. C'est à {player.pseudo} de jouer. La couleur est {color}\x02")
        else:
            current_card = COLORS[game.current_card.split(
                '_')[0]] + ' ' + game.current_card

            await bot.send(f"PRIVMSG {channel} :\x02{pseudo} a passé son tour. C'est à {player.pseudo} de jouer. La carte est {current_card}\x02")

        if len(player.hand) == 1 and not player.uno: # Le joueur n'a pas dit UNO
            cards = []
            for _ in range(2):  # Piocher 2 cartes
                new_card = game.deck.draw()
                player.add_card(new_card)

                cards.append(COLORS[new_card.split('_')[0]] + ' ' + new_card)
            drawed_string = ", ".join(cards)

            await bot.send(f"PRIVMSG {channel} :\x02{player.pseudo} n'a pas dit UNO ! Tu pioche 2 cartes.\x02")
            await bot.send(f"NOTICE {player.pseudo} :\x02Tu as pioché les cartes suivantes : {drawed_string}.\x02")
            
        nb_card = len(player.hand)
        cards = []
        for i in range(nb_card):
            card = player.hand[i]
            # Ajouter le carré de couleur correspondant
            card = COLORS[card.split('_')[0]] + ' ' + card
            cards.append(card)
        hand_string = ", ".join(cards)

        await bot.send(f"NOTICE {player.pseudo} :\x02Voici ta main : {hand_string}\x02")
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

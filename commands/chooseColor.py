from utils.colors import COLORS


async def chooseColor(game, bot, pseudo, channel, msg):
    """ Traiter la réponse du bot à l'action Choisir une couleur

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
        msg (string): Message du joueur composant son action
    """

    success, message = await game.choose_color(bot, pseudo, channel, msg)

    if success:
        color = game.current_card.split('_')[0]
        color = COLORS[color] + ' ' + color

        player = game.players[game.current_player]

        await bot.send(f"PRIVMSG {channel} :\x02La nouvelle couleur est {color}. C'est à {player.pseudo} de jouer.\x02")

        if len(player.hand) == 1 and not player.uno: # Le joueur n'a pas dit UNO
            cards = []
            for _ in range(2):  # Piocher 2 cartes
                new_card = game.deck.draw()
                player.add_card(new_card)

                cards.append(COLORS[new_card.split('_')[0]] + ' ' + new_card)
            drawed_string = ", ".join(cards)

            await bot.send(f"\x02PRIVMSG {channel} :{player.pseudo} n'a pas dit UNO ! Tu pioche 2 cartes.\x02")
            await bot.send(f"\x02NOTICE {player.pseudo} :Tu as pioché les cartes suivantes : {drawed_string}.\x02")

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
            case "NOT_ASKED":
                await bot.send(f"PRIVMSG {channel} :\x02Ce n'est pas le moment de choisir une couleur.\x02")

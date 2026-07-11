from utils.colors import COLORS


async def play(game, bot, pseudo, channel, msg):
    """ Traiter la réponse du bot à l'action Jouer une carte

    Parameters:
        game (Uno): Partie de Uno 
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
        msg (string): Message du joueur composant son action
    """

    success, message = await game.play(bot, pseudo, channel, msg)

    if success:
        print ('current card : ', game.current_card)
        current_card = COLORS[game.current_card.split(
            '_')[0]] + ' ' + game.current_card
        player = game.players[game.current_player]

        await bot.send(f"PRIVMSG {channel} :La nouvelle carte est {current_card}. C'est à {player.pseudo} de jouer.")

        nb_card = len(player.hand)
        cards = []
        for i in range(nb_card):
            card = player.hand[i]
            # Ajouter le carré de couleur correspondant
            card = COLORS[card.split('_')[0]] + ' ' + card
            cards.append(card)
        hand_string = ", ".join(cards)

        await bot.send(f"NOTICE {player.pseudo} :Voici ta main : {hand_string}")
    else:
        match message:
            case "NOT_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie n'a pas encore commencé.")
            case "NOT_YOUR_TURN":
                await bot.send(f"PRIVMSG {channel} :Ce n'est pas à ton tour de jouer.")
            case "NO_CARD":
                await bot.send(f"PRIVMSG {channel} :Tu n'as choisit aucune carte.")
            case "NOT_IN_HAND":
                await bot.send(f"PRIVMSG {channel} :Cette carte n'est pas dans ta main.")
            case "INVALID":
                await bot.send(f"PRIVMSG {channel} :Ce coup est invalide.")

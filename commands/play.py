from utils.colors import COLORS

async def play(game, bot, pseudo, channel, msg):
    success, message = game.play(pseudo, msg)

    if success:
        current_card = game.current_card
        current_card = COLORS[current_card.split('_')[0]] + ' ' + current_card

        player = game.players[game.current_player]

        await bot.send(f"PRIVMSG {channel} :La nouvelle carte est {current_card}. C'est à {player.pseudo} de jouer.")

        nb_card = len(player.hand)
        hand_string = ''
        for i in range(nb_card):
            card = player.hand[i]
            card = COLORS[card.split('_')[0]] + ' ' + card # Ajouter le carré de couleur correspondant
            if i + 1 == nb_card:  # Dernière carte de la main
                hand_string += card
            else:
                hand_string += card + ', '

        await bot.send(f"NOTICE {player.pseudo} :Voici ta main : {hand_string}")
    else:
        match message:
            case "NOT_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie n'a pas encore commencé.")
            case "NOT_YOUR_TURN":
                await bot.send(f"PRIVMSG {channel} :Ce n'est pas à ton tour de jouer.")
            case "NOT_IN_HAND":
                await bot.send(f"PRIVMSG {channel} :Cette carte n'est pas dans ta main.")
            case "INVALID":
                await bot.send(f"PRIVMSG {channel} :Ce coup est invalide.")

from utils.colors import COLORS


async def chooseColor(game, bot, pseudo, channel, msg):
    success, message = game.choose_color(pseudo, msg)

    if success:
        color = game.current_card.split('_')[0]
        color = COLORS[color] + ' ' + color

        player = game.players[game.current_player]

        await bot.send(f"PRIVMSG {channel} :La nouvelle couleur est {color}. C'est à {player.pseudo} de jouer.")

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
            case "NOT_ASKED":
                await bot.send(f"PRIVMSG {channel} :Ce n'est pas le moment de choisir une couleur.")
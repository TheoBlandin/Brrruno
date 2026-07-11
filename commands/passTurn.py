from utils.colors import COLORS


async def passTurn(game, bot, pseudo, channel):
    success, message = game.pass_turn(pseudo)

    if success:
        player = game.players[game.current_player]
        if game.current_card.split('_')[1] == 'undefined': # Cas où le joueur précédent a passé son tour après un joker
            color = game.current_card.split('_')[0]
            color = COLORS[color] + ' ' + color

            await bot.send(f"PRIVMSG {channel} :{pseudo} a passé son tour. C'est à {player.pseudo} de jouer. La couleur est {color}")
        else:
            current_card = COLORS[game.current_card.split(
                '_')[0]] + ' ' + game.current_card
            
            await bot.send(f"PRIVMSG {channel} :{pseudo} a passé son tour. C'est à {player.pseudo} de jouer. La carte est {current_card}")

        nb_card = len(player.hand)
        hand_string = ''
        for i in range(nb_card):
            card = player.hand[i]
            # Ajouter le carré de couleur correspondant
            card = COLORS[card.split('_')[0]] + ' ' + card
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
            case "MOVE_POSSIBLE":
                await bot.send(f"PRIVMSG {channel} :Tu peux jouer sans passer ton tour.")
            case "DRAW_POSSIBLE":
                await bot.send(f"PRIVMSG {channel} :Essaye de piocher une carte avant de passer ton tour.")

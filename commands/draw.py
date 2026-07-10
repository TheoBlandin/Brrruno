from utils.colors import COLORS

async def draw(game, bot, pseudo, channel):
    success, message = game.draw_card(pseudo)

    if success:
        player = game.players[game.current_player]
        nb_card = len(player.hand)

        hand_string = ''
        drawed_card = ''
        for i in range(nb_card):
            card = player.hand[i]
            card = COLORS[card.split('_')[0]] + ' ' + card # Ajouter le carré de couleur correspondant
            if i + 1 == nb_card:  # Dernière carte de la main
                hand_string += card
                drawed_card = card
            else:
                hand_string += card + ', '

        await bot.send(f"NOTICE {player.pseudo} :Tu as pioché la carte {drawed_card}. Voici ta main : {hand_string}")
    else:
        match message:
            case "NOT_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie n'a pas encore commencé.")
            case "NOT_YOUR_TURN":
                await bot.send(f"PRIVMSG {channel} :Ce n'est pas à ton tour de jouer.")
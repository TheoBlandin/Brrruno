async def startGame(game, bot, channel):
    success, message = game.start_game()

    if success:
        await bot.send(f"PRIVMSG {channel} :La partie va commencer !")

        for p in game.players:
            hand_string = ''

            for i in range(7):
                if i + 1 == 7:  # Dernière carte de la main
                    hand_string += p.hand[i]
                else:
                    hand_string += p.hand[i] + ', '

            await bot.send(f"NOTICE {p.pseudo} :Voici ta main : {hand_string}")
        
        await bot.send(f"PRIVMSG {channel} :La première carte est : {game.current_card}. C'est à {game.players[game.current_player].pseudo} de jouer.")

    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie est déjà en cours")
            case "NOT_ENOUGH":
                await bot.send(f"PRIVMSG {channel} :Il faut deux joueurs minimum pour lancer une partie. Taper !join pour rejoindre la partie")

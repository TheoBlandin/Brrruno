async def startGame(game, bot, channel):
    success, message = game.start_game()

    if success:
        await bot.send(f"PRIVMSG {channel} :La partie va commencer !")
    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie est déjà en cours")
            case "NOT_ENOUGH":
                await bot.send(f"PRIVMSG {channel} :Il faut deux joueurs minimum pour lancer une partie. Taper !join pour rejoindre la partie")

async def quitGame(game, bot, user, channel):
    success, message = game.remove_player(user)

    if success:
        await bot.send(f"PRIVMSG {channel} :{user} a quitté la partie.")
    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :Tu ne peux pas quitter une partie en cours.")
            case "NOT_IN":
                await bot.send(f"PRIVMSG {channel} :Tu n'es pas enregistré comme joueur.")

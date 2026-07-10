async def joinGame(game, bot, user, channel):
    success, message = game.add_player(user)

    if success:
        await bot.send(f"PRIVMSG {channel} :{user} a rejoint la partie.")
    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie est déjà en cours.")
            case "ALREADY_IN":
                await bot.send(f"PRIVMSG {channel} :Tu es déjà dans la partie.")

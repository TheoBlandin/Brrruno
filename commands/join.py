async def joinGame(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Rejoindre la partie

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.add_player(pseudo)

    if success:
        await bot.send(f"PRIVMSG {channel} :\x02{pseudo} a rejoint la partie.\x02")
    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :\x02La partie est déjà en cours.\x02")
            case "ALREADY_IN":
                await bot.send(f"PRIVMSG {channel} :\x02Tu es déjà dans la partie.\x02")

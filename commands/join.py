async def joinGame(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Rejoindre la partie

    Parameters:
        game (Uno): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.add_player(pseudo)

    if success:
        await bot.send(f"PRIVMSG {channel} :{pseudo} a rejoint la partie.")
    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie est déjà en cours.")
            case "ALREADY_IN":
                await bot.send(f"PRIVMSG {channel} :Tu es déjà dans la partie.")

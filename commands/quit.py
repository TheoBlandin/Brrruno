async def quitGame(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Quitter la partie

    Parameters:
        game (Game): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.remove_player(pseudo)

    if success:
        await bot.send(f"PRIVMSG {channel} :\x02{pseudo} a quitté la partie.\x02")
    else:
        match message:
            case "NOT_IN":
                await bot.send(f"PRIVMSG {channel} :\x02Tu n'es pas enregistré comme joueur.\x02")

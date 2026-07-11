async def quitGame(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Quitter la partie

    Parameters:
        game (Uno): Partie de Uno
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.remove_player(pseudo)

    if success:
        await bot.send(f"PRIVMSG {channel} :{pseudo} a quitté la partie.")
    else:
        match message:
            case "ALREADY_STARTED":
                await bot.send(f"PRIVMSG {channel} :Tu ne peux pas quitter une partie en cours.")
            case "NOT_IN":
                await bot.send(f"PRIVMSG {channel} :Tu n'es pas enregistré comme joueur.")

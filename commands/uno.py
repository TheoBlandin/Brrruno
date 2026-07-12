async def uno(game, bot, pseudo, channel):
    """ Traiter la réponse du bot à l'action Crier UNO

    Parameters:
        game (Game): Partie de Uno 
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    success, message = game.uno(pseudo)

    if success:
        await bot.send(f"PRIVMSG {channel} :Attention, {pseudo} n'a plus qu'une seule carte...")
    else:
        match message:
            case "NOT_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie n'a pas encore commencé.")
            case "NO_UNO":
                await bot.send(f"PRIVMSG {channel} :Tu ne peux pas crier UNO maintenant.")
            case "ALREADY_UNO":
                await bot.send(f"PRIVMSG {channel} :Tu as déjà dit UNO.")

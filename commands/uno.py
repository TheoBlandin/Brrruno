async def uno(game, pseudo):
    """ Traiter la réponse du bot à l'action Crier UNO

    Parameters:
        game (Game): Partie de Uno 
        pseudo (str): Pseudo du joueur ayant effectué l'action
    """

    success, message = game.uno(pseudo)

    if success:
        await game.bot.send(f"PRIVMSG {game.channel} :\x02Attention, {pseudo} n'a plus qu'une seule carte...\x02")
    else:
        match message:
            case "NOT_STARTED":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02La partie n'a pas encore commencé.\x02")
            case "NO_UNO":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02Tu ne peux pas crier UNO maintenant.\x02")
            case "ALREADY_UNO":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02Tu as déjà dit UNO.\x02")

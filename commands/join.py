async def joinGame(game, pseudo):
    """ Traiter la réponse du bot à l'action Rejoindre la partie

    Parameters:
        game (Game): Partie de Uno
        pseudo (str): Pseudo du joueur qui rejoint la partie
    """

    success, message = game.add_player(pseudo)

    if success:
        await game.bot.send(f"PRIVMSG {game.channel} :\x02{pseudo} a rejoint la partie.\x02")
    else:
        match message:
            case "ALREADY_STARTED":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02La partie est déjà en cours.\x02")
            case "ALREADY_IN":
                await game.bot.send(f"PRIVMSG {game.channel} :\x02Tu es déjà dans la partie.\x02")

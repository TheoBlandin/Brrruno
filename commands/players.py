async def seePlayers(game, bot, channel):
    """ Traiter la réponse du bot à l'action Voir la liste des joueurs

    Parameters:
        game (Game): Partie de Uno 
        bot (IRCClient): Bot de jeu connecté à l'IRC
        channel (str): Salon dans lequel le joueur a effectué l'action
    """

    nbPlayers = len(game.players)

    if nbPlayers == 0:
        await bot.send(f"PRIVMSG {channel} :\x02Il n'y a aucun joueur dans la partie.\x02")

    else:
        players_string = ''
        for i in range(nbPlayers):
            if i + 1 == nbPlayers:  # Dernier joueur de la liste
                players_string += game.players[i].pseudo + '.'
            else:
                players_string += game.players[i].pseudo + ', '

        await bot.send(f"PRIVMSG {channel} :\x02Voici la liste des joueurs : {players_string}\x02")

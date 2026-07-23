async def seePlayers(game):
    """ Traiter la réponse du bot à l'action Voir la liste des joueurs

    Parameters:
        game (Game): Partie de Uno 
    """

    nbPlayers = len(game.players)

    if nbPlayers == 0:
        await game.bot.send(f"PRIVMSG {game.channel} :\x02Il n'y a aucun joueur dans la partie.\x02")

    else:
        players = []
        for i in range(nbPlayers):
            player = game.players[i].pseudo
            players.append(player)
        players_string = ", ".join(players)

        await game.bot.send(f"PRIVMSG {game.channel} :\x02Voici la liste des joueurs : {players_string}\x02")

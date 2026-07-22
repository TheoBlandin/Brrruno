async def seePlayers(game):
    """ Traiter la réponse du bot à l'action Voir la liste des joueurs

    Parameters:
        game (Game): Partie de Uno 
    """

    nbPlayers = len(game.players)

    if nbPlayers == 0:
        await game.bot.send(f"PRIVMSG {game.channel} :\x02Il n'y a aucun joueur dans la partie.\x02")

    else:
        players_string = ''
        for i in range(nbPlayers):
            if i + 1 == nbPlayers:  # Dernier joueur de la liste
                players_string += game.players[i].pseudo + '.'
            else:
                players_string += game.players[i].pseudo + ', '

        await game.bot.send(f"PRIVMSG {game.channel} :\x02Voici la liste des joueurs : {players_string}\x02")

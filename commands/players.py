async def seePlayers(game, bot, channel):
    players = game.see_players()
    nbPlayers = len(players)

    if nbPlayers == 0:
        await bot.send(f"PRIVMSG {channel} :Il n'y a aucun joueur d'enregistrer")

    else :
        players_string = ''
        for i in range(nbPlayers):
            if i + 1 == nbPlayers: # Dernier joueur de la liste
                players_string += players[i].pseudo
            else:
                players_string += players[i].pseudo + ', '

        await bot.send(f"PRIVMSG {channel} :Liste des joueurs : {players_string}")

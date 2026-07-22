async def seeCommands(game, pseudo):
    await game.bot.send(f"NOTICE {pseudo} :\x02Liste des commandes :\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Rejoindre la partie : !go\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Quitter la partie : !quit\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Voir la liste des joueurs : !joueurs\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Jouer une carte : !jouer <carte> <option> ou !j <carte> <option> avec <carte> le nom de la carte, et <option> la couleur choisie dans le cadre d'une carte joker\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Piocher une carte : !pioche ou !p\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Crier UNO : !uno\x02")
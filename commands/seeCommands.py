async def seeCommands(game, pseudo):
    await game.bot.send(f"NOTICE {pseudo} :\x02Liste des commandes :\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Rejoindre la partie : !go\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Quitter la partie : !quit\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Voir la liste des joueurs : !joueurs\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Jouer une carte : !jouer <carte> ou !j <carte> avec <carte> le nom de la carte\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Piocher une carte : !pioche ou !p\x02")
    await game.bot.send(f"NOTICE {pseudo} :\x02Crier UNO : !uno\x02")
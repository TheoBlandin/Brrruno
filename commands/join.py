async def handleJoin(game, bot, user, channel): 
    print("handle join")
    if game.add_player(user):
        await bot.send(f"PRIVMSG {channel}:{user} a rejoint la partie")
    else:
        await bot.send(f"PRIVMSG {channel}:{user} ne peut pas rejoindre la partie")
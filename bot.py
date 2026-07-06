import asyncio

import config
from irc.client import IRCClient

from game.uno import Uno


async def main():
    game = Uno() # initialiser le jeu

    bot = IRCClient(
        config.SERVER,
        config.PORT,
        config.NICK,
        config.USERNAME,
        config.REALNAME,
        game
    )

    await bot.connect()

    await bot.loop()

    


asyncio.run(main())
import asyncio

import config
from irc.client import IRCClient

from game.game import Game


async def main():
    game = Game()  # initialiser le jeu

    bot = IRCClient(
        config.SERVER,
        config.PORT,
        config.NICK,
        config.USERNAME,
        config.REALNAME,
        game
    )

    try:
        await bot.connect()
        await bot.loop()

    except KeyboardInterrupt:
        print("Arrêt du bot...")

        bot.running = False
        await bot.stop()

asyncio.run(main())

import asyncio

import config
from irc import IRCClient


async def main():

    bot = IRCClient(
        config.SERVER,
        config.PORT,
        config.NICK,
        config.USERNAME,
        config.REALNAME
    )

    await bot.connect()

    await bot.loop()


asyncio.run(main())
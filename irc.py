import asyncio
import config

class IRCClient:

    def __init__(self, server, port, nick, username, realname):
        self.server = server
        self.port = port
        self.nick = nick
        self.username = username
        self.realname = realname

        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.server,
            self.port
        )

        await self.send(f"NICK {self.nick}")
        await self.send(f"USER {self.username} 0 * :{self.realname}")

    async def send(self, message):
        print(">> [W]", message)
        self.writer.write((message + "\r\n").encode())
        await self.writer.drain()

    async def recv(self):
        line = await self.reader.readline()
        return line.decode(errors="ignore").strip()

    async def loop(self):
        registered = False

        while True:
            message = await self.recv()

            print("<< [R]", message)

            if message.startswith("PING"):
                await self.send(f"PONG {message.split()[1]}")

            if not registered and "001" in message:
                registered = True

                for channel in config.CHANNELS:
                    await self.send(f"JOIN {channel}")
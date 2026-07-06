import asyncio

import config

from irc.parser import parse_privmsg

from commands.join import joinGame
from commands.players import seePlayers

class IRCClient:
    def __init__(self, server, port, nick, username, realname, game):
        self.server = server
        self.port = port
        self.nick = nick
        self.username = username
        self.realname = realname

        self.game = game

        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.server,
            self.port
        )

        await self.send(f"NICK {self.nick}")
        await self.send(f"USER {self.username} 0 * :{self.realname}")

    async def stop(self):
        try:
            await self.send("QUIT :Bot shutdown")

            if self.writer:
                self.writer.close()
                await self.writer.wait_closed()

        except Exception as e:
            print("Erreur arrêt bot:", e)

    async def send(self, message):
        print(">> [W]", message)
        self.writer.write((message + "\r\n").encode())
        await self.writer.drain()

    async def recv(self):
        line = await self.reader.readline()
        return line.decode(errors="ignore").strip()

    # Commandes
    async def handle_join(self, user, channel):
        await joinGame(self.game, self, user, channel)

    async def handle_players(self, channel):
        await seePlayers(self.game, self, channel)

    async def loop(self):
        registered = False
        self.running = True

        while self.running:
            message = await self.recv()
            print("<< [R]", message)

            # PING / PONG
            if message.startswith("PING"):
                await self.send(f"PONG {message.split()[1]}")

            # Connexion + rejoindre les channels
            if not registered and "001" in message:
                registered = True

                await self.send(f"PART #accueil")

                for channel in config.CHANNELS:
                    await self.send(f"JOIN {channel}")

            # Gestion des commandes
            parsed = parse_privmsg(message)
            if parsed:
                user, channel, msg = parsed

               
                match msg:
                    case "!join": # Rejoindre la partie
                        await self.handle_join(user, channel)
                    case "!players": # Voir la liste des joueurs
                        await self.handle_players(channel)

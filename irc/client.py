import asyncio

import config

from irc.parser import parse_privmsg

from commands.join import joinGame
from commands.quit import quitGame
from commands.players import seePlayers
from commands.start import startGame
from commands.play import play
from commands.draw import draw
from commands.chooseColor import chooseColor

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

        if not line:
            self.running = False
            return ""

        return line.decode(errors="ignore").strip()

    # Commandes
    async def handle_join(self, user, channel):
        await joinGame(self.game, self, user, channel)

    async def handle_quit(self, user, channel):
        await quitGame(self.game, self, user, channel)

    async def handle_players(self, channel):
        await seePlayers(self.game, self, channel)

    async def handle_start(self, channel):
        await startGame(self.game, self, channel)

    async def handle_play(self, user, channel, msg):
        await play(self.game, self, user, channel, msg)

    async def handle_draw(self, user, channel):
        await draw(self.game, self, user, channel)

    async def handle_choose_color(self, user, channel, msg):
        await chooseColor(self.game, self, user, channel, msg)

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
                    await self.send(f"PRIVMSG {channel} :Prêts pour une partie de Uno ? Taper !join pour rejoindre la partie")

            # Gestion des commandes
            parsed = parse_privmsg(message)
            if parsed:
                user, channel, msg = parsed

                match msg.lower():
                    case "!join": # Rejoindre la partie
                        await self.handle_join(user, channel)
                    case "!quit": # Quitter la partie
                        await self.handle_quit(user, channel)
                    case "!players": # Voir la liste des joueurs
                        await self.handle_players(channel)
                    case "!start": # Lancer la partie
                        await self.handle_start(channel)
                    case c if c.startswith("!play") : # Jouer une carte
                        await self.handle_play(user, channel, msg)
                    case "!draw": # Piocher une carte
                        await self.handle_draw(user, channel)
                    case c if c in ["!rouge", "!vert", "!bleu", "!jaune"]: # Choisir une couleur en cas de carte Joker
                        await self.handle_choose_color(user, channel, msg)

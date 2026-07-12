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
from commands.passTurn import passTurn
from commands.uno import uno


class IRCClient:
    """ Bot à connecter à l'IRC 

    Attributes:
        server (str): Lien du serveur IRC auquel le bot doit se connecter
        port (str): Port auquel le bot doit se connecter
        nick (str): Nick du bot
        username (str): Pseudo du bot
        realname (str): Vrai nom du bot
        game (Game): Partie de Uno gérée par le bot
        reader (asyncio.StreamReader | None): Stream permettant de lire les messages envoyés sur le serveur IRC
        writer (asyncio.StreamWriter | None): Stream permettant d'écrire sur le serveur IRC  
    """

    def __init__(self, server, port, nick, username, realname, game):
        """ Initialiser le bot

        Parameters:
            server (str): Lien du serveur IRC auquel le bot doit se connecter
            port (str): Port auquel le bot doit se connecter
            nick (str): Nick du bot
            username (str): Pseudo du bot
            realname (str): Vrai nom du bot
            game (Game): Partie de Uno gérée par le bot
        """

        self.server = server
        self.port = port
        self.nick = nick
        self.username = username
        self.realname = realname

        self.game = game

        self.reader = None
        self.writer = None

    async def connect(self):
        """ Connection au serveur IRC """

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
        """ Écrire un message sur le serveur IRC

        Parameters:
            message (str): Message à écrire
        """

        self.writer.write((message + "\r\n").encode())
        await self.writer.drain()

    async def recv(self):
        """ Recevoir un message depuis le serveur IRC 

        Returns:
            (str): Message lu sur le serveur IRC
        """

        line = await self.reader.readline()

        if not line:
            self.running = False
            return ""

        return line.decode(errors="ignore").strip()

    async def loop(self):
        """ Boucle d'actions du bot """

        registered = False
        self.running = True

        while self.running:
            message = await self.recv()

            # PING / PONG
            if message.startswith("PING"):
                await self.send(f"PONG {message.split()[1]}")

            # Connexion + rejoindre les channels
            if not registered and "001" in message:
                registered = True

                # Quitter l'accueil auto-join par défaut
                await self.send(f"PART #accueil")

                for channel in config.CHANNELS:
                    await self.send(f"JOIN {channel}")
                    await self.send(f"PRIVMSG {channel} :Prêts pour une partie de Uno ? Tapez !join pour rejoindre la partie")

            # Gestion des commandes
            parsed = parse_privmsg(message)
            if parsed:
                user, channel, msg = parsed

                match msg.lower():
                    case "!join":  # Rejoindre la partie
                        await joinGame(self.game, self, user, channel)
                    case "!quit":  # Quitter la partie
                        await quitGame(self.game, self, user, channel)
                    case "!players":  # Voir la liste des joueurs
                        await seePlayers(self.game, self, channel)
                    case "!start":  # Lancer la partie
                        await startGame(self.game, self, channel)
                    case c if c.startswith("!play"):  # Jouer une carte
                        await play(self.game, self, user, channel, msg)
                    case "!draw":  # Piocher une carte
                        await draw(self.game, self, user, channel)
                    # Choisir une couleur en cas de carte Joker
                    case c if c in ["!rouge", "!vert", "!bleu", "!jaune"]:
                        await chooseColor(self.game, self, user, channel, msg)
                    case "!pass":  # Passer ton tour
                        await passTurn(self.game, self, user, channel)
                    case "!uno":  # Crier UNO
                        await uno(self.game, self, user, channel)

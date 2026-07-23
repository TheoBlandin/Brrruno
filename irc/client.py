import asyncio

from commands import seeCommands
from commands.chooseColor import chooseColor
import config

from irc.parser import parse_privmsg

from commands.join import joinGame
from commands.quit import quitGame
from commands.players import seePlayers
from commands.play import play
from commands.draw import draw
from commands.uno import uno


class IRCClient:
    """Bot à connecter à l'IRC

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
        """Initialiser le bot

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
        """Connection au serveur IRC"""

        self.reader, self.writer = await asyncio.open_connection(self.server, self.port)

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
        """Écrire un message sur le serveur IRC

        Parameters:
            message (str): Message à écrire
        """

        self.writer.write((message + "\r\n").encode())
        await self.writer.drain()

    async def recv(self):
        """Recevoir un message depuis le serveur IRC

        Returns:
            (str): Message lu sur le serveur IRC
        """

        line = await self.reader.readline()

        if not line:
            self.running = False
            return ""

        return line.decode(errors="ignore").strip()

    async def loop(self):
        """Boucle d'action du bot"""

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

                await self.send(f"JOIN {config.CHANNEL}")
                await self.send(
                    f"PRIVMSG {config.CHANNEL} :\x02Prêts pour une nouvelle partie ? Tapez !go pour rejoindre la partie !\x02"
                )
                self.game.build(self, config.CHANNEL)

            # Gestion des commandes
            parsed = parse_privmsg(message)
            if parsed:
                user, _, msg = parsed

                match msg.lower():
                    case "!go":  # Rejoindre la partie
                        await joinGame(self.game, user)
                    case "!quit":  # Quitter la partie
                        await quitGame(self.game, user)
                    case "!joueurs":  # Voir la liste des joueurs
                        await seePlayers(self.game)
                    case c if c.startswith("!jouer ") or c.startswith("!j "):  # Jouer une carte
                        await play(self.game, user, msg)
                    case c if c == "!pioche" or c == "!p":  # Piocher une carte
                        await draw(self.game, user)
                    case c if c in ["!rouge", "!vert", "!bleu", "!jaune"]: # Choisir une couleur
                        await chooseColor(self.game, user, msg)
                    case "!uno":  # Crier UNO
                        await uno(self.game, user)
                    case "!help": # Aide de jeu
                        await seeCommands(self, user)

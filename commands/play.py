from utils.colors import COLORS
from utils.winners import WINNERS


async def play(game, bot, pseudo, channel, msg):
    """ Traiter la réponse du bot à l'action Jouer une carte

    Parameters:
        game (Game): Partie de Uno 
        bot (IRCClient): Bot de jeu connecté à l'IRC
        pseudo (str): Pseudo du joueur ayant effectué l'action
        channel (str): Salon dans lequel le joueur a effectué l'action
        msg (string): Message du joueur composant son action
    """

    success, message = await game.play(bot, pseudo, channel, msg)

    if success:
        current_card = COLORS[game.current_card.split(
            '_')[0]] + ' ' + game.current_card
        player = game.players[game.current_player]

        await bot.send(f"PRIVMSG {channel} :La nouvelle carte est {current_card}. C'est à {player.pseudo} de jouer.")

        if len(player.hand) == 1 and not player.uno: # Le joueur n'a pas dit UNO
            cards = []
            for _ in range(2):  # Piocher 2 cartes
                new_card = game.deck.draw()
                player.add_card(new_card)

                cards.append(COLORS[new_card.split('_')[0]] + ' ' + new_card)
            drawed_string = ", ".join(cards)

            await bot.send(f"PRIVMSG {channel} :{player.pseudo} n'a pas dit UNO ! Tu pioche 2 cartes.")
            await bot.send(f"NOTICE {player.pseudo} :Tu as pioché les cartes suivantes : {drawed_string}.")

        nb_card = len(player.hand)
        cards = []
        for i in range(nb_card):
            card = player.hand[i]
            # Ajouter le carré de couleur correspondant
            card = COLORS[card.split('_')[0]] + ' ' + card
            cards.append(card)
        hand_string = ", ".join(cards)

        await bot.send(f"NOTICE {player.pseudo} :Voici ta main : {hand_string}")
    else:
        match message:
            case "NOT_STARTED":
                await bot.send(f"PRIVMSG {channel} :La partie n'a pas encore commencé.")
            case "NOT_YOUR_TURN":
                await bot.send(f"PRIVMSG {channel} :Ce n'est pas à ton tour de jouer.")
            case "NO_CARD":
                await bot.send(f"PRIVMSG {channel} :Tu n'as choisit aucune carte.")
            case "NOT_IN_HAND":
                await bot.send(f"PRIVMSG {channel} :Cette carte n'est pas dans ta main.")
            case "INVALID":
                await bot.send(f"PRIVMSG {channel} :Ce coup est invalide.")
            case "END":
                winners = []
                for i in range(game.finish_order):
                    winner = WINNERS[i] if i < 3 else '' + game.finish_order[i]
                    winners.append(winner)
                winner_string = ", ".join(winners)

                await bot.send(f"PRIVMSG {channel} :La partie est terminée, voici le classement : {winner_string}")
                await bot.send(f"PRIVMSG {channel} :Prêts pour une nouvelle partie ? Tapez !join pour rejoindre la partie !")

def parse_privmsg(raw):
    """ Parser un message envoyé sur l'IRC pour être traité par le bot

    Parameters:
        raw (str): Message envoyé sur l'IRC
        
    Returns:
        (str): Pseudo du joueur ayant envoyé le message
        (str): Salon dans lequel le message a été envoyé
        (str): Message envoyé
    """
    
    if "PRIVMSG" not in raw:
        return None

    prefix, msg = raw.split(" :", 1)
    parts = prefix.split()

    user = parts[0][1:].split("!")[0]
    channel = parts[2]

    return user, channel, msg

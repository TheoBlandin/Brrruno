def parse_privmsg(raw):
    if "PRIVMSG" not in raw:
        return None

    prefix, msg = raw.split(" :", 1)
    parts = prefix.split()

    user = parts[0][1:].split("!")[0]
    channel = parts[2]

    return user, channel, msg
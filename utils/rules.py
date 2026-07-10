def checkPlay(game, player_card):
    current_color, current_symbol = game.current_card.split('_')
    player_color, player_symbol = player_card.split('_')

    # Carte joker
    if player_color == "joker":
        return (True, "OK")

    # Même couleur
    if current_color == player_color :
        return (True, "OK")
    
    # Même symbole
    if current_symbol == player_symbol :
        return (True, "OK")
    
    return (False, "INVALID")
    

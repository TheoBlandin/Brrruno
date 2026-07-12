# BrrrUno
Bot IRC pour jouer au Uno

## Configuration
À la racine du projet, créer un fichier .env avec ces variables :
``` py
SERVER = "test.example.fr" # URL de votre serveur IRC
CHANNELS = "#channel_1","#channel_2" # Noms des channels à rejoindre, sans espace entre les virgules
```

## Commandes
**!join** : Rejoindre la partie

**!quit** : Quitter la partie

**!players** : Liste des joueurs

**!start** : Lancer la partie

**!play <card>** : Jouer une carte

**!draw** : Piocher une carte

**!pass** : Passer son tour

**!rouge** ou **!vert** ou **!bleu** ou **!jaune** : Choisir une couleur suite à une carte Joker

**!uno** : Crier UNO
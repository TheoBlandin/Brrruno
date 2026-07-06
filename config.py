# config.py

import os
from dotenv import load_dotenv, dotenv_values

load_dotenv() 

SERVER = os.getenv("SERVER")
PORT = 6667

NICK = "Brrruno"
USERNAME = "Brrruno"
REALNAME = "bot-uno"

CHANNELS = [
    "#Amie"
]
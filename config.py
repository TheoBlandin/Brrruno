# config.py

import os
from dotenv import load_dotenv, dotenv_values

load_dotenv() 

SERVER = os.getenv("SERVER")
PORT = 6667

NICK = "BrrrUno"
USERNAME = "BrrrUno"
REALNAME = "bot-uno"

CHANNEL = os.getenv("CHANNEL")
import json
import random
import uuid
from player import PlayersConfig
from ships  import ShipsConfig


class GameConfig:
    def __init__(self,
                 player=PlayersConfig(),
                 ships=ShipsConfig()
                 ):
        self.player = player
        self.ships = ships

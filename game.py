from player import PlayersConfig
from ships  import ShipsConfig
import utils

class GameConfig:
    def __init__(self,
                 player=PlayersConfig(),
                 ships=ShipsConfig(),
                 ):
        self.player = player
        self.ships = ships
        self.game_config_data = utils.loadconfig('data/game_config.json', 'settings')


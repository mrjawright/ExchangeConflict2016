from collections import Counter
import random
import uuid
from game import GameConfig
from player import Player
from ships import ship

class Universe:
    def __init__(self, name, graph, config=GameConfig()):
        self.name = name
        self.graph = graph
        self.redis = None
        self.pubsub = None
        self.config = config
        self.players = {}
        self.ships = {}

    def create_player(self, name, password, key):
        sid = uuid.uuid4()
        self.players[name] = Player(self,
                                    name,
                                    password,
                                    key,
                                    credits=self.config.player.initial_credits,
                                    current_node=self.config.player.initial_sector_id,
                                    ship=sid)
        self.create_ship('merchant_cruiser', sid)

    def reset_player(self, name):
        sid = uuid.uuid4()
        player_to_reset = self.players[name]
        self.players[name] = Player(self,
                                    player_to_reset.name,
                                    player_to_reset.password,
                                    player_to_reset.key,
                                    credits=self.config.player.initial_credits,
                                    current_node=self.config.player.initial_sector_id,
                                    ship=sid)
        self.create_ship('merchant_cruiser', sid)

    def create_ship(self, stype, sid):
        ship_config = {}
        for k, v in self.config.ships.types[stype].items():
            ship_config[k] = v
        player_ship = ship(stype, sid, ship_config)
        self.ships[sid] = player_ship

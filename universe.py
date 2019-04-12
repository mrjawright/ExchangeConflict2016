from collections import Counter
import json
import random
import uuid
from game import GameConfig
from player import Player


class Universe:
    def __init__(self, name, graph, config=GameConfig()):
        self.name = name
        self.graph = graph
        self.config = config
        self.players = {}
        self.ships = {}

    def create_player(self, name):
        """Add a new player to the game"""
        sid = uuid.uuid4()
        self.players[name] = Player(self,
                                    name,
                                    credits=self.config.player.initial_credits,
                                    current_node=self.config.player.initial_sector_id,
                                    ship=sid)
        self.create_ship('merchant_cruiser', sid)

    def create_ship(self, stype, sid):
        ship = {}
        for k, v in self.config.ships.types[stype].items():
            ship[k] = v
        ship['holds_current'] = ship['holds_min']
        ship['cargo'] = {}
        self.ships[sid] = ship

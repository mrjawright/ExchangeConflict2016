from collections import Counter
import uuid


class PlayersConfig:
    def __init__(self,
                 initial_sector_id=1,
                 initial_ship_type="merchant_cruiser",
                 initial_credits=5000
                 ):
        self.initial_credits = initial_credits
        self.initial_ship_type = initial_ship_type
        self.initial_sector_id = initial_sector_id

class Player:
    def __init__(self, game, name, password, key, credits, current_node, ship):
        self.uuid = uuid.uuid4()
        self.universe = game
        self.experience = 0
        self.name = name
        self.password = password
        self.key = key
        self.wallet = credits
        self.ship_current = ship
        self.sectors_visited = Counter()
        self.current_node = current_node

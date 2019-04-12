import json

class ShipsConfig:
    def __init__(self, ship_data='data/ships.json'):
        f = open(ship_data, 'r')
        self.types = json.loads(f.read())['types']
        f.close()


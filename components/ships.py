import string
import random
import utils
import components.commodities as commodities


class ShipsConfig:
    def __init__(self, ship_data='data/ships.json'):
        self.types = utils.loadconfig(ship_data, 'types')

class ship:

    def __repr__(self):
        return '%s: %s \n\tHolds: %i\n\tCargo: %s\n\tShields:%s\n\tFighters:%s' % (
            self.uuid, self.name, self.holds, self.cargo, self.shields, self.fighters)

    def __init__(self, model, uuid,  ship_config):
        self.cargo = {} 
        available_commodities = commodities.commodities('data/commodities.json').items
        for commodity in available_commodities:
            self.cargo[commodity.name] = 0
        self.uuid = uuid
        self.model = model
        n = random.choices([3,3,3,3,4,4,4],k=1)
        name_prefix = ''.join(random.choices(string.ascii_uppercase, k=n[0]))
        name_suffix = ''.join(random.choices(string.digits, k=n[0]+1))
        self.name = name_prefix + '-' + name_suffix
        self.holds = ship_config['holds_default']
        self.fighters = ship_config['fighters_default']
        self.shields = ship_config['shields_default']
        

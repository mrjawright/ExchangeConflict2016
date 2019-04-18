import json
import random
from utils import bimodal


class upgrades:
    items = []
    def __init__(self, item_data='data/upgrades.json'):
        f = open(item_data, 'r')
        items_config_data = json.loads(f.read())['items']
        f.close()
        for x in items_config_data:
           attr = items_config_data[x]
           u = upgrade(x, (attr["price_distribution_low"]["low"],attr["price_distribution_low"]["high"],attr["price_distribution_low"]["mode"]),
                            (attr["price_distribution_high"]["low"],attr["price_distribution_high"]["high"],attr["price_distribution_high"]["mode"]),
                         attr["unit_range_low"],attr["unit_range_high"])
           self.items.append(u)


class upgrade:

    def __init__(self,
                 name,
                 price_distribution_low,
                 price_distribution_high,
                 unit_range_low,
                 unit_range_high,
                 **kwargs):
        self.name = name
        self.price_distribution_low = price_distribution_low
        self.price_distribution_high = price_distribution_high
        self.unit_range_low = unit_range_low
        self.unit_range_high = unit_range_high
        self.units = kwargs.get('units', None)
        self.price_buy = kwargs.get('units', None)
        self.price_sell = kwargs.get('units', None)

    def __repr__(self):
        return "Upgrade('{}', {}, {}, {}, {})".format(self.name,
                                                        self.price_distribution_low,
                                                        self.price_distribution_high,
                                                        self.unit_range_low,
                                                        self.unit_range_high)

    def generate(self):
        self.units = random.randint(self.unit_range_low, self.unit_range_high)
        x = round(bimodal(*self.price_distribution_low, *self.price_distribution_high), 0)
        y = round(bimodal(*self.price_distribution_high, *self.price_distribution_low), 0)
        self.price_buy = min(x, y)
        self.price_sell = max(x, y)


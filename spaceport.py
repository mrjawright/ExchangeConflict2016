from commodities import commodity
from commodities import commodities
from random import random
import config
import json

class spaceport(object):
    items = None
    tags = None

    def show_items(self, get_inputs=False):
        # Attempting to make showing the prices reusable.  The inputs and displayed
        # prices could get out of sync during a trade session if the items in the
        # station changed.
        print("\n{:^14} {:^16} {:^10}".format('Items', 'Prices (B/S)', 'Supply'))
        print("{:^14} {:^16} {:^10}".format('¯' * 5, '¯' * 13, '¯' * 6))

        if get_inputs:
            commodity_choices = {}
            counter = 1
            valid_item_inputs = []
        for item in self['items']:
            item = self['items'][item]
            if get_inputs:
                commodity_choices[counter] = item.name
                valid_item_inputs.append(str(counter))
                counter += 1
            prices = f"{item.price_buy:<7}/{item.price_sell:>7}"
            print(f"{item.name:<14} {prices:^16} {item.units:^10}")
        if get_inputs:
            return commodity_choices, valid_item_inputs


    def trade(self, UNI, player):
        # display commodities
        commodity_choices, valid_item_inputs = show_items(self, get_inputs=True)
        # do trading
        trade = ''
        while trade.upper() != 'Q':
            trade = input('Enter your choice (1-4 or Q)? ')
            player_ship = UNI.ships[player.ship_current]
            # find max cargo space available for trade
            cargo_used = sum([player_ship['cargo'][item] for item in player_ship['cargo']])
            available_holds = player_ship["holds_current"] - cargo_used
            print(f'\nYou have {player.wallet} credits and {available_holds} empty cargo holds.\n')
            if trade in valid_item_inputs:
                # get commodity data
                choice = self['items'][commodity_choices[int(trade)]]
                mode = input("Do you want to (B)uy or (S)ell?")
                if mode.upper() == 'B':
                    wallet_max_buy = player.wallet // choice.price_sell
                    max_buy = int(min(wallet_max_buy, available_holds))
                    to_buy = input(f"We are selling up to {choice.units} of {choice.name} at {choice.price_sell} per unit.  You have {available_holds} available holds.\nHow many do you want to buy? [{max_buy}] ")
                    try:
                        to_buy_number = int(to_buy)
                    except ValueError:
                        to_buy_number = 0
                    if to_buy == '':
                        to_buy_number = max_buy
                    if to_buy_number > 0 and to_buy_number <= max_buy:
                        if choice.name not in player_ship['cargo']:
                            player_ship['cargo'][choice.name] = to_buy_number
                        else:
                            player_ship['cargo'][choice.name] += to_buy_number
                        wallet_change = choice.price_sell * to_buy_number
                        player.wallet -= wallet_change
                        self['items'][choice.name].units -= to_buy_number
                        print(f'\n You bought {to_buy_number} units of {choice.name} for {wallet_change}.')
                        show_items(station)
                    else:
                        print("\nThat's not a valid amount!\n")
                        show_items(station)
                elif mode.upper() == 'S':
                    max_sell = player_ship['cargo'].get(choice.name, 0)
                    to_sell = input(f"We are buying {choice.name} at {choice.price_buy} per unit.  You have {max_sell} available units.\nHow many do you want to sell? [{max_sell}] ")
                    try:
                        to_sell_number = int(to_sell)
                    except ValueError:
                        to_sell_number = 0
                    if to_sell == '':
                        to_sell_number = max_sell
                    elif to_sell_number > 0 and to_sell_number <= max_sell:
                        player_ship['cargo'][choice.name] -= to_sell_number
                        #player.wallet += choice.price_buy * to_sell_number
                        wallet_change = choice.price_buy * to_sell_number
                        player.wallet += wallet_change
                        self['items'][choice.name].units += to_sell_number
                        print(f'\n You sold {to_sell_number} units of {choice.name} for {wallet_change}.')
                        show_items(self)
                    else:
                        print("\nThat's not a valid amount!\n")
                        show_items(self)

    def gettags(station):
        f = open('data/station_tags.json', 'r')
        tags_config_data = json.loads(f.read())['tags']
        f.close()
        for key in tags_config_data:
            use_tag = True
            for type in tags_config_data[key]:
                attr = tags_config_data[key][type]
                if type in station['items']:
                    station_items = station['items'][type]
                    #is this type relevant to the tag? were any checks used?
                    check_type = False
                    #if so, did the checks pass?
                    #we prime with true and use AND joins so one success doesn't give a false positive
                    type_check_passed = True
                    #print("type: %s buy_min: %s buy_max: %s price_buy: %s" % (type, attr['buy_min'],attr['buy_max'],station_items.price_buy))
                    #print("type: %s sell_min: %s sell_max: %s price_sell: %s" % (type, attr['sell_min'],attr['sell_max'],station_items.price_sell))
                    if attr['buy_min']>0: 
                        check_type = True
                        type_check_passed = type_check_passed and (attr['buy_min'] < station_items.price_buy)
                    if attr['buy_max']>0:
                        check_type = True
                        type_check_passed = type_check_passed and (attr['buy_max'] > station_items.price_buy)
                    if attr['sell_min']>0:
                        check_type = True
                        type_check_passed = type_check_passed and (attr['sell_min'] < station_items.price_sell)
                    if attr['sell_max']>0:
                        check_type = True
                        type_check_passed = type_check_passed and (attr['sell_max'] > station_items.price_sell)
                    #print("type:%s used:%s passed:%s" % (type, check_type, type_check_passed))
                    if check_type:
                        use_tag = (use_tag and type_check_passed)
            #print("%s %s"% (key,use_tag))
            if use_tag and not key in station['tags']:
                station['tags'].append(key)
        #print(station['tags'])
        return station['tags']

    @staticmethod
    def stationgen():
        """Generates station."""
        port_commodities = commodities().items
        port_upgrades = commodities('data/upgrades.json').items

        station = {'items': {commodity.name: commodity
                             for commodity in port_commodities},
                   'upgrades': {upgrade.name: upgrade
                                for upgrade in port_upgrades} }
        items = station['items']
        for item in items:
            items[item].generate()
        station['tags'] = []
        station['has_hangar'] = False 
        hangar_type=None
        for item in items:
            item = items[item]
            if item.price_buy > item.price_sell:
                item.price_sell = round(item.price_buy * uniform(1,3))
        station['tags'] = spaceport.gettags(station)
        if "PRODUCTION" in station['tags']:
            if random()>0.5:
                hangar_type="SCRAPYARD"
                station['has_hangar'] = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if "ORBITAL HYDROPONICS" in station['tags']:
            if random()>0.75 and not station['has_hangar']:
                hangar_type = "GARAGE"
                station['has_hangar'] = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if "ICE MINING" in station['tags']:
            if random()>0.66 and not station['has_hangar']:
                hangar_type = "MAINTENANCE"
                station['has_hangar'] = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if "SUPER BUY" in station['tags']:
            if not station['has_hangar']:
                hangar_type = "SPACE STATION"
                station['has_hangar'] = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if station['has_hangar']:
            station['tags'].append(hangar_type)

        print(station['tags'])
        return station

    def __init__(self, node = None, station = None):
        if not node == None:
            station = stationgen(node)
        self.items = station['items']
        self.has_hangar = station['has_hangar']
        self.upgrades = station['upgrades']
        self.tags = station['tags']



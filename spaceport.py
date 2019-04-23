from commodities import commodity
from commodities import commodities
from datetime import datetime
from ships import ShipsConfig
from ships import ship
from random import random
import config
import json

def prompt(choices):
    clock = datetime.now().strftime('%H:%M:%S')
    menu = ''
    for c in choices:
        menu+=str(c)
    selection= input("Command [TL={}]:[{}](?=Help) : ".format(clock,menu))
    return selection.upper()

class spaceport(object):
    items = None
    upgrades = None
    has_hangar = False
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
        x = 1
        for item in self.items:
            item = self.items[item]
            if get_inputs:
                commodity_choices[counter] = item.name
                valid_item_inputs.append(str(counter))
                counter += 1
            prices = f"{item.price_buy:<7}/{item.price_sell:>7}"
            item_option=f"[{x}] {item.name}"
            print(f"{item_option:<14} {prices:^16} {item.units:^10}")
            x+=1
        if get_inputs:
            return commodity_choices, valid_item_inputs


    def trade(self, UNI, player):
        # display commodities
        commodity_choices, valid_item_inputs = self.show_items(get_inputs=True)
        commodity_choices['Q'] = 'Quit'
        # do trading
        trade = ''
        while trade.upper() != 'Q':
            trade = prompt(commodity_choices)
            player_ship = UNI.ships[player.ship]
            # find max cargo space available for trade
            cargo_used = sum([player_ship.cargo[item] for item in player_ship.cargo])
            available_holds = player_ship.holds - cargo_used
            print(f'\nYou have {player.wallet} credits and {available_holds} empty cargo holds.\n')
            if trade in valid_item_inputs:
                # get commodity data
                choice = self.items[commodity_choices[int(trade)]]
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
                        if choice.name not in player_ship.cargo:
                            player_ship.cargo[choice.name] = to_buy_number
                        else:
                            player_ship.cargo[choice.name] += to_buy_number
                        wallet_change = choice.price_sell * to_buy_number
                        player.wallet -= wallet_change
                        self.items[choice.name].units -= to_buy_number
                        print(f'\n You bought {to_buy_number} units of {choice.name} for {wallet_change}.')
                        self.show_items()
                    elif to_buy_number == 0:
                        print("\nStop wasting my time!\n")
                    else:
                        if to_buy_number > wallet_max_buy:
                            print("\nYou can't afford it!\n")
                        elif to_buy_number > available_holds:
                            print("\nYou don't have enough holds!\n")
                        else:
                            print("\nI'm not sure what you mean by that.\n")
                        self.show_items()
                elif mode.upper() == 'S':
                    max_sell = player_ship.cargo.get(choice.name, 0)
                    to_sell = input(f"We are buying {choice.name} at {choice.price_buy} per unit.  You have {max_sell} available units.\nHow many do you want to sell? [{max_sell}] ")
                    try:
                        to_sell_number = int(to_sell)
                    except ValueError:
                        to_sell_number = 0
                    if to_sell == '':
                        to_sell_number = max_sell
                    if to_sell_number > 0 and to_sell_number <= max_sell:
                        player_ship.cargo[choice.name] -= to_sell_number
                        wallet_change = choice.price_buy * to_sell_number
                        player.wallet += wallet_change
                        self.items[choice.name].units += to_sell_number
                        print(f'\n You sold {to_sell_number} units of {choice.name} for {wallet_change}.')
                        self.show_items()
                    elif to_sell_number == 0:
                        print("\nStop wasting my time!\n")
                    else:
                        if to_sell_number > max_sell:
                            print("\nYou don't have that much!\n")
                        else:
                            print("\nI don't know what you mean by that.\n")
                        self.show_items()
            else:
                print("Huh? I don't have any of that.")



    def show_upgrades(self, get_inputs=False):
        # Attempting to make showing the prices reusable.  The inputs and displayed
        # prices could get out of sync during a trade session if the items in the
        # station changed.
        print("\n{:^14} {:^16} {:^10}".format('Items', 'Prices (B/S)', 'Supply'))
        print("{:^14} {:^16} {:^10}".format('¯' * 5, '¯' * 13, '¯' * 6))

        if get_inputs:
            upgrade_choices = {}
            counter = 1
            valid_upgrade_inputs = []
        x = 1
        for item in self.upgrades:
            item = self.upgrades[item]
            if get_inputs:
                upgrade_choices[counter] = item.name
                valid_upgrade_inputs.append(str(counter))
                counter += 1
            prices = f"{item.price_buy:<7}/{item.price_sell:>7}"
            item_option=f"[{x}] {item.name}"
            print(f"{item_option:<14} {prices:^16} {item.units:^10}")
            x+=1
        if get_inputs:
            return upgrade_choices, valid_upgrade_inputs

    def dock(self, UNI, player):
        # display commodities
        upgrade_choices, valid_upgrade_inputs = self.show_upgrades(get_inputs=True)
        upgrade_choices['Q'] = 'Quit'
        shipsconfig = ShipsConfig()
        # do trading
        trade = ''
        while trade.upper() != 'Q':
            trade = prompt(upgrade_choices)
            player_ship = UNI.ships[player.ship]
            print(f'\nYou have {player.wallet} credits.')
            if trade in valid_upgrade_inputs:
                # get commodity data
                choice = self.upgrades[upgrade_choices[int(trade)]]
                mode = input("Do you want to (B)uy or (S)ell?")
                if mode.upper() == 'B':
                    
                    wallet_max_buy = player.wallet // choice.price_sell
                    hullconfig = ShipsConfig().types[player_ship.model]
                    ship_limit = 0
                    if choice.name == 'fighters':
                        ship_limit = hullconfig['fighters_max'] - player_ship.fighters
                    if choice.name == 'holds':
                        ship_limit = hullconfig['holds_max'] - player_ship.holds
                    if choice.name == 'shields':
                        ship_limit = hullconfig['shields_max'] - player_ship.shields
                    max_buy = lambda x: ship_limit if x > ship_limit else x 
                    default_buy = max_buy(wallet_max_buy)
                    if ship_limit <= 0:
                         default_buy = 0
                    to_buy = input(f"We are selling up to {choice.units} of {choice.name} at {choice.price_sell} per unit.  You can buy {default_buy}.\nHow many do you want? [{default_buy}] ")
                    try:
                        to_buy_number = int(to_buy)
                    except ValueError:
                        to_buy_number = 0
                    if to_buy == '':
                        to_buy_number = default_buy
                    if to_buy_number > 0 and to_buy_number <= default_buy:
                        wallet_change = choice.price_sell * to_buy_number
                        player.wallet -= wallet_change
                        self.upgrades[choice.name].units -= to_buy_number
                        print(f'\n You bought {to_buy_number} units of {choice.name} for {wallet_change}.')
                        if choice.name == 'fighters':
                            UNI.ships[player.ship].fighters  += to_buy_number
                        if choice.name == 'holds':
                            UNI.ships[player.ship].holds  += to_buy_number
                        if choice.name == 'shields':
                            UNI.ships[player.ship].shields += to_buy_number 
                        self.show_upgrades()
                    elif to_buy_number == 0:
                        print("\nStop wasting my time!\n")
                    else:
                        if to_buy_number > wallet_max_buy:
                            print("\nYou can't afford it!\n")
                        elif to_buy_number > ship_limit:
                            print("\nYour ship can't handle that many!\n")
                        else:
                            print("\nI'm not sure what you mean by that.\n")
                        self.show_upgrades()
                elif mode.upper() == 'S':
                    max_sell = 0
                    to_sell = input(f"We are buying {choice.name} at {choice.price_buy} per unit.  You have {max_sell} available units.\nHow many do you want to sell? [{max_sell}] ")
                    try:
                        to_sell_number = int(to_sell)
                    except ValueError:
                        to_sell_number = 0
                    if to_sell == '':
                        to_sell_number = max_sell
                    if to_sell_number > 0 and to_sell_number <= max_sell:
                        player_ship.cargo[choice.name] -= to_sell_number
                        wallet_change = choice.price_buy * to_sell_number
                        player.wallet += wallet_change
                        self.items[choice.name].units += to_sell_number
                        print(f'\n You sold {to_sell_number} units of {choice.name} for {wallet_change}.')
                        self.show_upgrades()
                    elif to_sell_number == 0:
                        print("\nStop wasting my time!\n")
                    else:
                        if to_sell_number > max_sell:
                            print("\nYou don't have that much!\n")
                        else:
                            print("\nI don't know what you mean by that.\n")
                        self.show_upgrades()
            else:
                print("Huh? I don't have any of those.")



    def gettags(self):
        f = open('data/station_tags.json', 'r')
        tags_config_data = json.loads(f.read())['tags']
        f.close()
        self.tags=[]
        for key in tags_config_data:
            use_tag = True
            for type in tags_config_data[key]:
                attr = tags_config_data[key][type]
                if type in self.items:
                    station_items = self.items[type]
                    #is this type relevant to the tag? were any checks used?
                    check_type = False
                    #if so, did the checks pass?
                    #we prime with true and use AND joins so one success doesn't give a false positive
                    type_check_passed = True
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
                    if check_type:
                        use_tag = (use_tag and type_check_passed)
            if use_tag and not key in self.tags:
                self.tags.append(key)
        return self.tags

    def stationgen(self):
        port_commodities = commodities('data/commodities.json').items
        port_upgrades = commodities('data/upgrades.json').items

        station = {'items': {commodity.name: commodity
                             for commodity in port_commodities},
                   'upgrades': {upgrade.name: upgrade
                                for upgrade in port_upgrades} }
        items = station['items']
       
        for item in items:
            items[item].generate()
        self.has_hangar = False 
        hangar_type=None
        for item in items:
            item = items[item]
            if item.price_buy > item.price_sell:
                item.price_sell = round(item.price_buy * uniform(1,3))
        self.items = items
        self.gettags()
        if "PRODUCTION" in self.tags:
            #if random()>0.5:
            if 1>0.5:
                hangar_type="SCRAPYARD"
                self.has_hangar = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if "ORBITAL HYDROPONICS" in self.tags:
            #if random()>0.75 and not station['has_hangar']:
            if 1>0.75 and not self.has_hangar:
                hangar_type = "GARAGE"
                self.has_hangar = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if "ICE MINING" in self.tags:
            #if random()>0.66 and not station['has_hangar']:
            if 1>0.66 and not self.has_hangar:
                hangar_type = "MAINTENANCE"
                self.has_hangar = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if "SUPER BUY" in self.tags:
            if not self.has_hangar:
                hangar_type = "SPACE STATION"
                self.has_hangar = True
                upgrades = station['upgrades']
                for item in upgrades:
                    upgrades[item].generate()
        if self.has_hangar:
            self.tags.append(hangar_type)
            self.upgrades = station['upgrades']
        return station

    def __init__(self):
        self.stationgen()



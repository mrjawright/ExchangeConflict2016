from datetime import datetime
from cryptography.fernet import Fernet
import os
import pickle
import uuid
from getpass import getpass
import networkx as nx
import redis
from random import random
from universe import Universe
from player import PlayersConfig
from game import GameConfig
import spaceport
#from trade import trade
import utils
import server 

def dump(universe):
    for node in universe.graph.node:
        print(f'Node: {node}')
        print("Neighbors:")
        for neighbor_node in sorted(universe.graph.neighbors(node)):
            print(f"\t{neighbor_node}")

def sector_menu_help():
    print("\nC to show your wallet and cargo\nL to land on a planet\nP to trade at a Port\nQ to quit\nS to use the scanner on planets and stars\nV to view jump history\nUse the number to warp to another sector or land on a planet.")

def station_menu_help():
    print("\nD to dock at a hangar\nT to trade at the port\nQ to quit and return to the sector\n")

def planet_menu_help():
    #print("\nA to allocate colonists to resources\nE to establish a colony\nL to leave cargo\nQ to quit\nT to take resources\n")
    print("\nC for the colony menu\nP to populate the planet with colonists\nQ to quit\n")

def prompt(node, choices):
    clock = datetime.now().strftime('%H:%M:%S')
    menu = ''
    for c in choices:
        menu+=c
    selection= input("Command [TL={}]:[{}] [{}](?=Help) : ".format(clock,node,menu))
    return selection.upper()

def save(current_player, UNI):
    if not current_player == None:
        UNI.redis.publish('GAMEWORLD', '{} leaves the game...'.format(current_player.name))
        UNI.pubsub.unsubscribe()
        UNI.pubsub = None
        UNI.redis = None
        for k in UNI.players:
            p = UNI.players[k]
            print(f"Player:{p}")
            print(f"\tShip:{UNI.ships[p.ship]}")
    pickle.dump(UNI, open(UNI.config.game_config_data['save_file'], 'wb'))
    raise SystemExit

def get_messages(current_player, UNI):
    #print(f'get_messages({current_player}, {UNI})')
    options = []
    messages = []
    header_message = ""
    current_node = current_player.current_node

    node_str = str(current_node)
    node_data = UNI.graph.node[current_node]

    exit_prompt = "Warps to Sector(s) : "
    
    if node_data.get('system') is not None:
        header_message = f"\nSector  : {current_node}\n"
        system_name = node_data['system'].name
        star = 'Star    : {} - {} Solar masses\n'.format(
            node_data['system'].star.name,
            node_data['system'].star.mass
        )
        messages.append(header_message)
        messages.append(star)
        system = node_data['system']
        if node_data['system'].planets is not None:
            bodies = [body.name + ' (' + body.type + ')'
                      for body
                      in node_data['system'].planets]
            messages.append('Bodies  : {}\n'.format(",  ".join(bodies)))
        options = ['C','L','P','Q','S','V','#']
    
        stations = node_data.get('station', None)
        if stations is not None:
            messages.append('Ports   : {}\n'.format("-".join(stations.tags)))
    elif '.' in node_str:
        info = str(current_node).split('.')
        parent = int(info[0])
        body = info[1]
        #Land
        body_info = UNI.graph.node[parent]["system"].planets[int(body)-1]
        star = UNI.graph.node[parent]["system"].star.name

        header_message = f"\nPlanet  : {body_info.name}\n"
        messages.append(header_message)

        messages.append(f'You\'ve landed on the {body_info.type} planet {body_info.name}\n')
        inventory_message = 'There are '
        use_and = False
        has_inventory = False
        for i in body_info.inventory:
            if body_info.inventory[i] is not None and body_info.inventory[i] > 0:
                if has_inventory == False:
                    has_inventory = True
                if use_and:
                    inventory_message.append(' and ')
                inventory_message.append(f'{body_info.inventory[i]} holds of {i}')
                use_and = True
        if has_inventory:
            messages.append(inventory_message)
        exit_prompt = "Take off and return to sector "
        options = ['C','P','Q','?']

    neighbors = sorted(UNI.graph.neighbors(current_player.current_node))
    visited_systems = current_player.sectors_visited.keys()
    jumps = " - ".join([str(x)
                        if x in visited_systems
                        else '({})'.format(str(x))
                        for x in neighbors
                        if '.' not in str(x)
                        ])
    messages.append(f"{exit_prompt} {jumps}\n")
    print("".join(messages))
    command = prompt(current_player.current_node, options)
    #print(f"return ({command.upper()}, {options})")
    return (command.upper(), options)

def scanner(current_node, UNI):
    print("Scanning....")
    if isinstance(current_node, int):
        node_data = UNI.graph.node[current_node]
        print(node_data['system']['star'])
    elif isinstance(current_node, float):
        sector, body = str(current_node).split('.')
        node_data = UNI.graph.node[int(sector)]
        print(node_data['system']['bodies'][int(body)-1])

def cargo(current_player, ship):
    message = 'Cargo:'
    for i in ship.cargo:
        message += '\n\t'
        message += f'{i}: {ship.cargo[i]}'
    print(f"{message}\nWallet: {current_player.wallet}")


def land(current_player, UNI):
    node = current_player.current_node
    node_str = str(node)
    node_data = UNI.graph.node[node]
    options = []
    bodies = []
    if node_data.get('system') is not None:
        for body in node_data['system'].planets:
            bodies.append(str(node)+'.'+body.planet_no+': '+body.name+' ('+body.type+')')
            options.append(str(node)+'.'+body.planet_no)
        for b in bodies:
            print(b)
        command = ''
        attempt=0
        while command not in options and attempt<3:
            command = input(f"Which planet:\n")
            attempt += 1
        if command in options:
            warp(current_player, command, UNI.graph.neighbors(current_player.current_node))
            command = ''
            options = []
            while not command == 'Q':
                (command, options) = get_messages(current_player,UNI)
                if command not in options and (command.isnumeric() or utils.is_float(command)):
                    warp(current_player, command, UNI.graph.neighbors(current_player.current_node))
                elif command == '?':
                    planet_menu_help()
                elif command == 'C':
                    print("Colony menu...")
                    break
                elif command == 'P':
                    print("Populate planet with colonists...")
                    break
                elif command == 'Q':
                    save(current_player, UNI)
                    break
        #else:
        #    warp(current_player, current_player.current_node, UNI.graph.neighbors(current_player.current_node))
    else:
        print("No suitable place to land!")

def port(current_player, UNI):
    node_data = UNI.graph.node[current_player.current_node]
    station = node_data.get('station', None)
    message = ''
    if station is not None:
        options = ['T','Q','?']
        t_message = "\n<T>rade at this Port"
        if station.has_hangar:
            options.insert(0,'D')
            message += "\n<D>ock to buy upgrades"
        message += t_message
        message += "\n<Q>uit, nevermind"
        option = ''
        while  option.upper() != 'Q' :
            print(message)
            option = prompt(current_player.current_node, options)
            if option.upper() == 'D':
               station.dock(UNI, current_player)
            if option.upper() == 'T':
               station.trade(UNI, current_player)
            if option == '?':
                station_menu_help()
    else:
        print("No ports in this sector!")

def warp(current_player, command, neighbors):
    try:
        destination= int(command)
    except ValueError:
        destination= float(command)
    if destination in neighbors:
        current_player.current_node = destination
        current_player.sectors_visited.update({current_player.current_node: 1})
    else:
        print(f"{command} is an invalid jump selection...try again!")

def login_player(universe):
    PLAYER = ""
    PASSWORD = ""
    command = ""
    attempt=0
    players = universe.players

    while PLAYER not in players and attempt <3:
        PLAYER = input('Enter valid player name: ')
        attempt += 1
    else:
        if  PLAYER not in players:
            PLAYER = None
            command = 'Q'
        else:
            selected_player = universe.players[PLAYER]
            cipher_suite = Fernet(selected_player.key)
            unencrypted_password = cipher_suite.decrypt(selected_player.password)
            attempt=0
            while not PASSWORD.encode('utf-8') == unencrypted_password and attempt < 3:
                PASSWORD = getpass('Password:')
                attempt += 1
                if not PASSWORD.encode('utf-8') == unencrypted_password:
                    print ('Wrong! Try Again!')
            if not PASSWORD.encode('utf-8') == unencrypted_password:
                command = 'Q'
                PLAYER = None
            else:
                print(f'{PLAYER}: Authorization accepted')
    return PLAYER, command

def new_player(universe):
    PLAYER = ""
    command = ""
    attempt = 0
    while PLAYER == "" and attempt <3:
        attempt += 1
        PLAYER = input('Enter a new player name: ')
        if PLAYER == "":
            print("Player name can not be empty")
        if PLAYER in universe.players:
            print("You can't use that name!")
            PLAYER = "" 
    else:
        if not PLAYER == "":
            if PLAYER in universe.players:
                print("You can't use that name!")
                PLAYER = None
            else:
                PASSWORD = ""
                attempt = 0
                while PASSWORD == "" and attempt<3: 
                    attempt += 1
                    PASSWORD = getpass('Password:')
                    if PASSWORD == "":
                        print("Password can not be empty")
                else:
                    if not PASSWORD == "":
                        key = Fernet.generate_key()       
                        cipher_suite = Fernet(key)
                        ciphered_text = cipher_suite.encrypt(PASSWORD.encode('utf-8'))
                        universe.create_player(PLAYER, ciphered_text, key)
                    else:   
                        PLAYER = None
                        command = 'Q'
        else:
            PLAYER = None
            command = 'Q'    
    return PLAYER,command


def main():
# MAIN
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    game_config_data = utils.loadconfig('data/game_config.json', 'settings')
    if os.path.exists(os.path.join(BASE_DIR,game_config_data['universe_file'])): 
        U = nx.readwrite.read_gpickle(game_config_data['universe_file'])

        rserver = server.redis_server()
        r = redis.StrictRedis(host=rserver.HOST,
                              port=rserver.PORT,
                              password=rserver.PASSWORD)
        p = r.pubsub()

        CENTRALITY_NODE = {v: k
                           for k, v
                           in nx.get_node_attributes(U, 'name').items()}['Centrality']

        
        UNI_PATH = game_config_data['save_file']
        if os.path.isfile(UNI_PATH):
            UNI = pickle.load(open(UNI_PATH, 'rb'))
        else:
            UNI = Universe('New Game', U, GameConfig(PlayersConfig(CENTRALITY_NODE)))

        UNI.redis = r
        UNI.pubsub = p 
        if len(UNI.players) == 0:
            (PLAYER,command) = new_player(UNI)
        else:
            selection = "" 
            PLAYER = None
            PASSWORD = None
            players = UNI.players.keys()
            attempt=0
            while selection.upper() not in ['N', 'E'] and attempt<3:
                selection = input("(N)ew player or (E)xisting player? ")
                attempt += 1
            else:
                if attempt == 3:
                    PLAYER = None
                    command = 'Q'
            if selection.upper() == 'E':
                (PLAYER,command) = login_player(UNI)
            elif selection.upper() == 'N':
                (PLAYER,command) = new_player(UNI)
            
        current_player = None
        if not PLAYER == None:
            current_player = UNI.players[PLAYER]
            p.subscribe('GAMEWORLD')
            r.publish('GAMEWORLD', '{} joins the game... {}'.format(current_player.name, uuid.uuid4()))
            command = None

        while command != 'Q':
            neighbors = UNI.graph.neighbors(current_player.current_node)
            options = []
            (command,options) = get_messages(current_player, UNI)
            if command not in options and (command.isnumeric() or utils.is_float(command)):
                warp(current_player, command, UNI.graph.neighbors(current_player.current_node))
            elif command == 'C':
                cargo(current_player, UNI.ships[current_player.ship])
            elif command == 'L':
                land(current_player, UNI)
            elif command == 'P':
                port(current_player, UNI)
            elif command == 'Q':
                save(current_player, UNI)
                break
            elif command == 'S':
                scanner(current_player, UNI)
            elif command == 'V':
                current_player.view_history()
            elif command == 'DUMP':
                dump(UNI)
            elif command == '?':
                sector_menu_help()
            else:
                print("Invalid command!")
    else:
        print("No universe file found. Run bigbang.py")

main()

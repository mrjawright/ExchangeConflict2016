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

def cargo(current_player, ship):
    message = 'Cargo:'
    for i in ship.cargo:
        message += '\n\t'
        message += f'{i}: {ship.cargo[i]}'
    print(f"{message}\nWallet: {current_player.wallet}")

def help():
    print("\n  This is the help menu.  P to trade at a Port, Q to quit, V to view jump history. C to show your wallet and cargo. S to use the scanner on planets and stars.")

def prompt(node, choices):
    clock = datetime.now().strftime('%H:%M:%S')
    menu = ''
    for c in choices:
        menu+=c
    selection= input("Command [TL={}]:[{}] [{}](?=Help) : ".format(clock,node,menu))
    return selection.upper()


def port(current_player, UNI):
    node_data = UNI.graph.node[current_player.current_node]
    station = node_data.get('station', None)
    message = ''
    if station is not None:
        choices = ['T','Q']
        t_message = "\n<T>rade at this Port"
        if station.has_hangar:
            choices = ['D','T','Q']
            message += "\n<D>ock to buy upgrades"
        message += t_message
        message += "\n<Q>uit, nevermind"
        selection = ''
        while  not selection.upper() == 'Q' :
            print(message)
            selection = prompt(current_player.current_node, choices)
            if selection.upper() == 'D':
                station.dock(UNI, current_player)
            if selection.upper() == 'T':
                station.trade(UNI, current_player)
    else:
        print("No ports in this sector!")

def scan(current_player, UNI):
    print("Scanning....")
    utils.scanner(current_player.current_node, UNI)

def warp(current_player, command, neighbors):
    try:
        target_node = int(command)
    except ValueError:
         target_node = float(command)
    if target_node in neighbors:
        current_player.current_node = target_node
        #if not target_node in current_player.sectors_visited:
            #current_player.experience += 1
        current_player.sectors_visited.update({current_player.current_node: 1})
    else:
        print("{} is an invalid jump selection...try again!".format(target_node))

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
    U = nx.readwrite.read_gpickle('multiverse/universe_body_nodes_experi.uni')
    rserver = server.redis_server()
    r = redis.StrictRedis(host=rserver.HOST,
                          port=rserver.PORT,
                          password=rserver.PASSWORD)
    p = r.pubsub()

    CENTRALITY_NODE = {v: k
                       for k, v
                       in nx.get_node_attributes(U, 'name').items()}['Centrality']

    UNI_PATH = 'multiverse/UNISAVE.pkl'

    if os.path.isfile(UNI_PATH):
        UNI = pickle.load(open(UNI_PATH, 'rb'))
    else:
        UNI = Universe('New Game', U, GameConfig(PlayersConfig(CENTRALITY_NODE)))
 
    if len(UNI.players) == 0:
        (PLAYER,command) = new_player(UNI)
    else:
        selection = "" 
        PLAYER = None
        PASSWORD = None
        players = UNI.players.keys()
        attempt=0
        while selection.upper() not in ['N', 'E'] and attempt<=3:
            selection = input("(N)ew player or (E)xisting player? ")
            attempt += 1
        else:
            if attempt > 3:
                PLAYER = None
                command = 'Q'
        if selection.upper() == 'E':
            attempt=0
            while PLAYER not in players and attempt <=3:
                PLAYER = input('Enter valid player name: ')
                attempt += 1
            else:
                if attempt > 3:
                    PLAYER = None
                    command = 'Q'
            PASSWORD = getpass('Password:')
            selected_player = UNI.players[PLAYER]
            cipher_suite = Fernet(selected_player.key)
            unencrypted_password = cipher_suite.decrypt(selected_player.password)
            attempt=0
            while not PASSWORD.encode('utf-8') == unencrypted_password and attempt<=3:
                attempt += 1
                print ('Wrong! Try Again!')
                PASSWORD = getpass('Password:')
            if not PASSWORD.encode('utf-8') == unencrypted_password or attempt > 3:
                command = 'Q'
                PLAYER = None
            else:
                print('{}: Authorization accepted'.format(PLAYER))
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
        print("".join(utils.get_messages(current_player.current_node, current_player, UNI)))
        command = prompt(current_player.current_node, ['C','P','Q','S','V','#'])
        #command = input("Command [TL={}]:[{}] [CPQSV#](?=Help) : ".format(clock, current_player.current_node))
        #command = command.upper()
        if command not in ['C', 'P', 'Q', 'V', '?'] and (command.isnumeric() or utils.is_float(command)):
            warp(current_player, command, UNI.graph.neighbors(current_player.current_node))
        elif command == 'V':
            current_player.view_history()
        elif command == 'C':
            cargo(current_player, UNI.ships[current_player.ship])
        elif command == 'S':
            scan(current_player, UNI)
        elif command == 'Q':
            break
        elif command == 'P':
            port(current_player, UNI)
        elif command == '?':
            help()
        else:
            print("Invalid command!")
    
    pickle.dump(UNI, open(UNI_PATH, 'wb'))
    if not current_player == None:
        r.publish('GAMEWORLD', '{} leaves the game...'.format(current_player.name))
        p.unsubscribe()
        for k in UNI.players:
            p = UNI.players[k]
            print(p)
            print(UNI.ships[p.ship])

main()

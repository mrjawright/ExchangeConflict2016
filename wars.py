from datetime import datetime
from cryptography.fernet import Fernet
import os
import pickle
import uuid

import networkx as nx
import redis

from universe import Universe
from player import PlayersConfig
from game import GameConfig
from trade import trade
import utils
import server 

def cargo(current_player):
    print(f"Cargo: {ship['cargo']}\n Wallet: {current_player.wallet}")

def help():
    print("\n  This is the help menu.  P to trade at a Port, Q to quit, V to view jump history. C to show your wallet and cargo. S to use the scanner on planets and stars.")

def port(current_player, UNI):
    node_data = UNI.graph.node[current_player.current_node]
    station = node_data.get('station', None)
    if station is not None:
        selection = ''
        print("\n<T> Trade at this Port\n<Q> Quit, nevermind")
        while selection.upper() not in ['T', 'Q']:
            selection = input('Enter your choice? ')
            if selection.upper() == 'T':
                trade(UNI, current_player, station)
    else:
        print("No ports in this sector!")

def scan(current_player, UNI):
    print("Scanning....")
    utils.scanner(current_player.current_node, UNI)

def view_history(current_player):
    print("Jump history: {}".format(current_player.sectors_visited))

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
        PLAYER = input('Enter a new player name: ')
        PASSWORD = input('Password:')
        key = Fernet.generate_key()       
        cipher_suite = Fernet(key)
        ciphered_text = cipher_suite.encrypt(PASSWORD.encode('utf-8'))
        UNI.create_player(PLAYER, ciphered_text, key)
    else:
        selection = "" 
        PLAYER = None
        PASSWORD = None
        players = UNI.players.keys()
        while selection.upper() not in ['N', 'E']:
            selection = input("(N)ew player or (E)xisting player? ")
        if selection.upper() == 'E':
            #print("Players: {}".format(UNI.players.keys()))
            while PLAYER not in players:
                PLAYER = input('Enter valid player name: ')
            PASSWORD = input('Password:')
            selected_player = UNI.players[PLAYER]
            cipher_suite = Fernet(selected_player.key)
            unencrypted_password = cipher_suite.decrypt(selected_player.password)
            attempt=1
            while not PASSWORD.encode('utf-8') == unencrypted_password and attempt<3:
                attempt +=1
                print ('Wrong! Try Again!')
                PASSWORD = input('Password:')
            if not PASSWORD.encode('utf-8') == unencrypted_password:
                command = 'Q'
                PLAYER = None
            else:
                print('{}: Authorization accepted'.format(PLAYER))
        elif selection.upper() == 'N':
            while PLAYER not in players:
                players = UNI.players.keys()
                PLAYER = input('Enter valid player name: ')
                if PLAYER in players:
                    print("You can't use that name!")
                    PLAYER = None
                else:
                    PASSWORD = input('Password:')
                    key = Fernet.generate_key()       
                    cipher_suite = Fernet(key)
                    ciphered_text = cipher_suite.encrypt(PASSWORD.encode('utf-8'))
                    UNI.create_player(PLAYER, ciphered_text, key)
                players = UNI.players.keys()
    current_player = None
    if not PLAYER == None:
        current_player = UNI.players[PLAYER]
        p.subscribe('GAMEWORLD')
        r.publish('GAMEWORLD', '{} joins the game... {}'.format(current_player.name, uuid.uuid4()))
        command = None

    while command != 'Q':
        neighbors = UNI.graph.neighbors(current_player.current_node)
        print("".join(utils.get_messages(current_player.current_node, current_player, UNI)))
        clock = datetime.now().strftime('%H:%M:%S')
        command = input("Command [TL={}]:[{}] [CPQSV#](?=Help) : ".format(clock, current_player.current_node))
        command = command.upper()
        if command not in ['C', 'P', 'Q', 'V', '?'] and (command.isnumeric() or utils.is_float(command)):
            warp(current_player, command, UNI.graph.neighbors(current_player.current_node))
        elif command == 'V':
            view_history()
        elif command == 'C':
            cargo(current_player)
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
        print(UNI.players)

main()

import sys
import os
import random
import time
import json
import uuid

import networkx as nx

from collections import Counter
from stargen import get_system_data, parse_system
from spaceport import spaceport

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

    def gen(total_systems=20, deadends=0, rings=0, connectivity=1):
        G = nx.Graph()
        print("...with {} systems, {} deadends, {} rings and {} connectivity.".format(total_systems, deadends, rings, connectivity))
        starchart = {}
        system_id = 1
        systems = 0
        potentials = [x for x in range(1, total_systems + 1)]
        connected = []
        dead = []

        f = open('data/star_names.txt', 'r')
        names = f.readlines()
        names = [line.strip() for line in names]
        f.close()

        if total_systems < 20:
            raise TooFewStarsError
        if 2 * deadends > total_systems / 2.0:
            raise ExcessiveDeadendsError

        while systems <= total_systems:
            if deadends > 0:
                print("Creating deadend.")
                G.add_node(system_id)
                G.add_node(system_id + 1)
                G.add_edge(system_id, system_id + 1)
                potentials.remove(system_id)
                connected.append(system_id)
                deadends -= 1
                system_id += 2
                dead.append(system_id)
                continue
            if rings != 0:
                ring_size = random.choice([3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 9, 11])
                ring_status = 'incomplete'
                ring = []
                while ring_status != 'complete':
                    if len(potentials) > ring_size and len(ring) < ring_size:
                        system = random.choice(potentials)
                        potentials.remove(system)
                        connected.append(system)
                        ring.append(system)
                    if len(ring) == ring_size:
                        ring_status = 'complete'
                print("Forming ring... {}".format(ring))
                for x in range(0, len(ring)):
                    if x == 0:
                        G.add_node(ring[-1])
                        G.add_node(ring[x+1])
                        G.add_edge(ring[-1], ring[x+1])
                    elif x == len(ring)-1:
                        G.add_node(ring[x-1])
                        G.add_node(ring[0])
                        G.add_edge(ring[x-1], ring[0])
                    else:
                        G.add_node(ring[x-1])
                        G.add_node(ring[x+1])
                        G.add_edge(ring[x-1], ring[x+1])
                rings -= 1
                continue

            if connectivity > 0:
                while potentials:
                    system = random.choice(potentials)
                    target = random.choice(connected)
                    G.add_edge(target, system)
                    potentials.remove(system)
                    connected.append(system)
                    continue

            systems += 1

        while not nx.is_connected(G):
            elements = nx.connected_component_subgraphs(G)
            choices = []
            for element in elements:
                choices.append(random.choice(list(element.nodes())))
            G.add_edge(choices[0], choices[1])
                
        # this places centrality in the node with the most jumps
        central = 1
        for node in G.nodes():
            if len(list(G.neighbors(node))) > central:
                central = node
        centrality_jumps = len(list(G.neighbors(central)))
        print("Centrality is node {} with {} jumps...".format(central,
                                                              centrality_jumps))

        # get random star name from star names list...if the list is empty use a uuid
        star_names = {}
        for x in range(0, total_systems):
            try:
                star_names[x+1] = names.pop(random.randint(0, len(names)-1))
            except ValueError:
                star_names[x+1] = str(uuid.uuid4())

        star_names[central] = 'Centrality'
        nx.set_node_attributes(G, 'name', hash(str(star_names)))
        G.node[central]['label_fill'] = 'red'
        G.node[central]['name'] = star_names[central]
        return G

    def getstations(target=30, total_systems=100, stock_volumes=.1):
        start = time.time()
        stations = []

        superbuys = 0
        superbuys_target = 3 + total_systems / 100

        productions = 0
        productions_target = 3 + total_systems / 100

        mines = 0
        mines_target = 5 + total_systems / 100
        while len(stations) < target:
            station = spaceport(station = spaceport.stationgen())
            if superbuys < superbuys_target:
                if 'SUPER BUY' in station.tags:
                    stations.append(station)
                    superbuys += 1
            elif superbuys >= superbuys_target and productions < productions_target:
                if 'PRODUCTION' in station.tags:
                    stations.append(station)
                    productions += 1
            elif superbuys >= superbuys_target and productions >= productions_target and mines < mines_target:
                if 'ORBITAL HYDROPONICS' in station.tags or 'ICE MINING' in station.tags:
                    stations.append(station)
            elif superbuys >= superbuys_target and productions >= productions_target and mines >= mines_target and "INVALID" not in station.tags:
                stations.append(station)
        stop = time.time()
        print("Stations took {} seconds to generate...".format(stop - start))
        return stations

    def universe(total_systems=20, deadends=0, rings=0, connectivity=1, stations='common', stock_volumes='normal'):
        station_density = {'sparse': .1,
                           'uncommmon': .15,
                           'common': .3,
                           'frequent': .45,
                           'dense': .6,
                           }

        stock = {'low': .1,
                 'normal': .2,
                 'high': .3,
                 'epic': .4}

        u = gen(total_systems, deadends, rings, connectivity)
        print("Universe built.")
        print("Creating stations...")
        stations = getstations(target=station_density[stations] * total_systems,
                               total_systems=total_systems,
                               stock_volumes=stock[stock_volumes])
        return u, stations
# MAIN
    def bigbang():
        print("Running program.")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        STARGEN_EXE='stargen'
        STARGEN_DATA_FILE='stargen'
        STARGEN_PATH = 'StarGen'
        STARGEN_EXE_PATH = os.path.join(STARGEN_PATH,STARGEN_EXE)
        STARGEN_DATA_PATH = os.path.join(STARGEN_PATH,'html')

        print("Generating Universe...")
        u, s = universe(50, 10, 3, 1, 'frequent', 'normal')

        print("Generate Planetary Systems...")
        # observed system types: 'Rock', 'Terrestrial', 'GasDwarf', 'Sub-Jovian', 'Jovian', 'Ice', 'Venusian', 'Martian', '1Face', 'Water', 'Asteroids'
        nodes = u.nodes()
        for node in nodes:
            u.node[node]['system'] = parse_system(get_system_data(BASE_DIR,
                                                                  STARGEN_PATH,
                                                                  STARGEN_EXE_PATH,
                                                                  STARGEN_DATA_PATH,
                                                                  STARGEN_DATA_FILE)
                                                  )

        print("Generate links from sectors to planetary bodies...")
        planet_types = {}
        for node in list(u.nodes()):
            for body in u.node[node]['system']['bodies']:
                body_node_label = float(str(node) + '.' + body['planet_no'])
                u.add_edge(node, body_node_label)
                btype = body['type']
                if btype not in planet_types:
                    planet_types[btype] = [body_node_label]
                else:
                    planet_types[btype].append(body_node_label)

        print("Placing stations...")
        nodes = u.nodes()
        try:
	        shuffled_nodes=random.sample(nodes,len(nodes))
	        nodes = shuffled_nodes
        except:
	        print("Unexpected error:", sys.exc_info()[0])

        planetary_data = {}

        # gather data for use in world building...ice mining on ice planets, etc
        planetary_data['ice_sources'] = planet_types.get('Water', []) + planet_types.get('Ice', [])
        planetary_data['terrestrials'] = planet_types.get('Terrestrial', [])

        for k in planetary_data:
            random.shuffle(planetary_data[k])

        for node in [sector for sector in nodes if isinstance(sector, int)]:
            if s != []:
                new_station = s.pop()
                # If it is an ice mining station place it on an appropriate body type
                if 'ICE MINING' in new_station.tags:
                    node = planetary_data['ice_sources'].pop()
                u.node[node]['station'] = new_station
                u.node[node]['fill'] = 'green'

        print("Universe created!")
        print("Writing Universe to file...")
        if not os.path.exists(os.path.join(BASE_DIR,'multiverse')):
	        os.mkdir(os.path.join(BASE_DIR,'multiverse'))
        nx.readwrite.write_gpickle(u, 'multiverse/universe_body_nodes_experi.uni')
        print("Removing saved games")
        if os.path.isfile('multiverse/UNISAVE.pkl'):
	        os.remove('multiverse/UNISAVE.pkl') 
        print("Complete!")

def __main__():
    universe.bigbang()

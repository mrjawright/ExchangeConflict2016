import sys
import random
import os
import subprocess
import uuid

import systems

def get_system_data(BASE_DIR,
                    STARGEN_PATH,
                    STARGEN_EXE_PATH,
                    STARGEN_DATA_PATH,
                    STARGEN_DATA_FILE):
    seed = random.randint(0, 10000000)
    stargen_command = " ".join([os.path.join(BASE_DIR, STARGEN_EXE_PATH),
                                "-s{}".format(seed), # Looks like I need to provide a seed, if I call this too fast it gets the same seed inside stargen
                                "-n1",
                                "-e",
                                "-g",
                                "-p"+os.path.join(BASE_DIR,STARGEN_DATA_PATH),
                                "-o"+STARGEN_DATA_FILE
                                # need code to handle moons in parser
                                # "-M"
                                ])
    data = ""
    try:
        #output = subprocess.call(stargen_command, cwd=os.path.join(BASE_DIR,STARGEN_PATH))
        output = subprocess.call([os.path.join(BASE_DIR, STARGEN_EXE_PATH), "-s{}".format(seed), "-n1", "-e", "-g", "-p"+os.path.join(BASE_DIR,STARGEN_DATA_PATH), "-o"+STARGEN_DATA_FILE], cwd=os.path.join(BASE_DIR,STARGEN_PATH))
        if output == 0:
            f = open(os.path.join(BASE_DIR,STARGEN_DATA_PATH,STARGEN_DATA_FILE)+'.csv', 'r')
            data = f.readlines()
            f.close()
        else:
            raise CalledProcessError(stargen_command)
    except FileNotFoundError as fnf:
        print(fnf.args)
        print(str(fnf.errno)+":"+ fnf.strerror)
        print(fnf.filename)
        print('with traceback %s' % fnf.with_traceback)
        raise fnf
    except Exception as exc:
        print("Unexpected error:", sys.exc_info()[0])
        raise exc
    return data


def parse_system(data):
    #Parses a stargen system csv file
    #returns a dict with star and bodies keys
    planetsconfig = systems.PlanetsConfig()
    data = [row.strip() for row in data]
    star = []
    bodies = []
    if len(data) == 0:
       raise Exception("No data returned") 

    headers_star = data[0]
    headers_planet = data[2]


    star_data = zip([col.strip().replace("'", "")
                     for col in headers_star.split(',')],
                    [col.strip().replace("'", "")
                     for col in data[1].split(',')])

    star = dict([col for col in star_data])
    # add an id
    star['id'] = uuid.uuid4()

    #  Remove WinStarGen/StarGen.exe from star name
    star['name'] = star['name'].split(' ')[1]

    for body in data[3:]:
        planet = None
        body_data = zip([col.strip().replace("'", "")
                         for col in headers_planet.split(',')],
                        [col.strip().replace("'", "")
                         for col in body.split(',')])
        body = dict([col for col in body_data])

        # Remove WinStarGen/StarGen.exe and Star name from body name
        body['planet_no'] = body['planet_no'].split(' ')[2]
        body['name'] = f"{star['name']}-{body['planet_no']}"
        # add an id
        body['id'] = uuid.uuid4()
        if body['type'] in planetsconfig.resource_config_data:
            planetconfig = planetsconfig.resource_config_data[body['type']]
            planet = systems.planet(body, planetconfig)
        if planet != None:
            bodies.append(planet)
    system = systems.system(systems.star(star), bodies)
    return system





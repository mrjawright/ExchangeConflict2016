import utils
#from stargen import get_system_data, parse_system

class PlanetsConfig:
    def __repr__(self):
        output = 'PlanetsConfig\n:'
        for p in self.resource_config_data:
            output += "\t"
            output += f'{p}:'
            output += "\n"
            for r in self.resource_config_data[p]:
                resource_config = self.resource_config_data[p][r]
                output+="\t\t"
                output+=f'{r}:'
                output+='\n\t\t\t'
                output += f"Low Unit Distribution :{resource_config['unit_distribution_low']}"
                output+='\n\t\t\t'
                output += f"High Unit Distribution :{resource_config['unit_distribution_high']}"
                output+='\n\t\t\t'
                output += f"Level of Effort Distribution :{resource_config['loe_distribution']}"
                output+='\n'
        return output
        
    def __init__(self, planet_data='data/planetary_resources.json'):
        self.resource_config_data = utils.loadconfig(planet_data, 'types')


class resource:

    def generate(self):
        self.units = round(utils.bimodal(*self.unit_distribution_low, *self.unit_distribution_high), 0)
        self.loe = round(utils.bimodal(*self.loe_distribution, *self.loe_distribution), 0)


    def __repr__(self):
        output = f"{self.name}:"
        output += "\n\t"
        output += f"Low Unit Distribution :{self.unit_distribution_low}"
        output += "\n\t"
        output += f"High Unit Distribution:{self.unit_distribution_high}"
        output += "\n\t"
        output += f"Level of Effort Distribution:{self.loe_distribution}"
        output += "\n\t"
        output += f"Units:{self.units}"
        output += "\n\t"
        output += f"Level of Effort:{self.loe}"
        output += "\n"
        return output
           
    def __init__(self,
                 name,
                 unit_distribution_low,
                 unit_distribution_high,
                 loe_distribution,
                 **kwargs):
        self.name = name
        self.unit_distribution_low = (unit_distribution_low['low'], 
                                      unit_distribution_low['high'], 
                                      unit_distribution_low['mode'])
        self.unit_distribution_high = (unit_distribution_high['low'], 
                                       unit_distribution_high['high'], 
                                       unit_distribution_high['mode'])
        self.loe_distribution = (loe_distribution['low'],
                                 loe_distribution['high'],
                                 loe_distribution['mode'])
        self.units = kwargs.get('units', None)
        self.loe = kwargs.get('loe', None)


class planet:

    def __repr__(self):
        output = f"Name: {self.name}:"
        output += "\n\t"
        output += f"planet_no: {self.planet_no}"
        output += "\n\t"
        output += f"id: {self.uuid}"
        output += "\n\t"
        output += f"type: {self.type}"
        output += "\n\t"
        output += f"owner: {self.owner}"
        output += "\n\t"
        output += f"owner: {self.owner}"
        output += "\n\t"
        output += f"resources: {self.resources}" 
        output += "\n\t"
        output += f"inventory: {self.inventory}" 
        output += "\n\t"
        output += f"planetary data: {self.planetary_data}" 
        return output

    def genresources(self, config_data):
        self.resources = {}
        self.inventory = {}
        for cd in config_data:
            r = resource(cd, config_data[cd]['unit_distribution_low'], 
                             config_data[cd]['unit_distribution_high'],
                             config_data[cd]['loe_distribution'])
            r.generate()
            self.resources[cd] = r
            self.inventory[cd] = 0

    def __init__(self, planetary_body, config_data):
        self.uuid = planetary_body['id']
        self.type = planetary_body['type']
        self.planet_no = planetary_body['planet_no']
        self.name = planetary_body['name']
        self.planetary_data = planetary_body
        self.owner = None
        self.genresources(config_data)
        self.colony_level = 0
        self.defense_level = 0
        self.planetary_shields = 0
        self.fighters = 0
        self.missles = 0



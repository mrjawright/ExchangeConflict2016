import networkx as nx
from networkx_viewer import Viewer
game_config_data = utils.loadconfig('data/game_config.json', 'settings')
u = nx.readwrite.read_gpickle(game_config_data['universe_file'])

app = Viewer(u)
app.mainloop()

import networkx as nx
import osmnx as ox
import numpy as np


class OSMEngine:
    def __init__(self):
        print("Initialize OSM Engine")
        self.G = ox.graph_from_place("Manhattan,New York USA", network_type="drive")
        self.G = ox.speed.add_edge_speeds(self.G)
        self.G = ox.speed.add_edge_travel_times(self.G)
        self.nodes, self.edges = ox.graph_to_gdfs(self.G)
    """
    def get_travel_time(self, nid_from, nid_to):
        return self.edges.loc[(nid_from, nid_to, 0)]['travel_time']
    """
    def get_location(self, nid):
        return self.nodes.loc[nid]['y':'x']

    def get_nearest_node(self, lat, lon):
        return ox.distance.nearest_nodes(self.G, X=lon, Y=lat)

    def generate_random_node(self):
        nid = np.random.choice(self.G.nodes)
        if nid not in self.edges.index:
            return self.generate_random_node()
        return nid

    def get_adjacent_node(self, nid):
        if nid in self.edges.index:
            adjacent_lst = list(map(lambda x: x[0], self.edges.loc[nid].index))
        else:
            adjacent_lst = []
        return adjacent_lst

    def get_shortest_route(self, nid_from, nid_to):
        return ox.distance.shortest_path(self.G, nid_from, nid_to, weight='travel_time')

    def get_travel_time(self, route, reject_time=None):
        travel_time = 0
        if reject_time:
            for i in range(len(route)-1):
                nid_from = route[i]
                nid_to = route[i+1]
                travel_time += self.edges.loc[(nid_from, nid_to, 0)]['travel_time']
                if travel_time >= reject_time:
                    return reject_time
        else:
            for i in range(len(route)-1):
                nid_from = route[i]
                nid_to = route[i+1]
                travel_time += self.edges.loc[(nid_from, nid_to, 0)]['travel_time']
        return travel_time


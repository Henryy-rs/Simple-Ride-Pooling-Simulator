import networkx as nx
import osmnx as ox
import numpy as np


class OSMEngine:
    def __init__(self):
        print("Initialize OSM Engine")
        self.G = ox.graph_from_place("Manhattan,New York USA", simplify=True, network_type="drive")
        # todo: delete dead end
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

    def get_travel_time(self, route, reject_time=None, to_list=False):
        travel_time = [0]
        if reject_time:
            for i in range(len(route)-1):
                nid_from = route[i]
                nid_to = route[i+1]
                travel_time.append(self.edges.loc[(nid_from, nid_to, 0)]['travel_time'])
                if sum(travel_time) >= reject_time:
                    return reject_time
        else:
            for i in range(len(route)-1):
                nid_from = route[i]
                nid_to = route[i+1]
                travel_time.append(self.edges.loc[(nid_from, nid_to, 0)]['travel_time'])
        if to_list:
            return travel_time
        else:
            return sum(travel_time)

    def get_shortest_travel_time(self, nid_from, nid_to, return_route=False, to_list=False, reject_time=None):
        route = self.get_shortest_route(nid_from, nid_to)
        if route is None:
            print("NO ROUTE FROM {} TO {}".format(nid_from, nid_to))
            if reject_time:
                return reject_time
            else:
                if return_route:
                    return -1, []
                else:
                    return -1
                # print(route, nid_from, nid_to)
                # raise Exception("There is no route. Use reject_time.")
        travel_time = self.get_travel_time(route, reject_time=reject_time, to_list=to_list)
        if return_route:
            return travel_time, route
        return travel_time

    def remove_dead_end(self):
        self.G
        return






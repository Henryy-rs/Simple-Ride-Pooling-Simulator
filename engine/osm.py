import os.path
import networkx as nx
import osmnx as ox
import numpy as np
import pickle
import sys
import matplotlib.pyplot as plt


sys.setrecursionlimit(100000)


class OSMEngine:
    def __init__(self, network_path=None, paths=""):
        print("Initialize OSM Engine")
        if network_path:
            self.G = ox.load_graphml(network_path)
            self.__map()
            self.G = nx.relabel.convert_node_labels_to_integers(self.G, label_attribute=int)
            self.nodes, self.edges = ox.graph_to_gdfs(self.G)
            self.dead_end = False
        else:
            self.G = ox.graph_from_place("Manhattan,New York USA", network_type="drive")
            self.__map()
            self.G = ox.speed.add_edge_speeds(self.G)
            self.G = ox.speed.add_edge_travel_times(self.G)
            self.G = nx.relabel.convert_node_labels_to_integers(self.G, label_attribute=int)
            self.nodes, self.edges = ox.graph_to_gdfs(self.G)
            self.dead_end = True
            self.__remove_dead_end()
            self.dead_end = False
        self.shortest_paths = None
        if os.path.exists(paths):
            with open(paths, "rb") as f:
                self.shortest_paths = pickle.load(f)

    def get_latlon(self, nid):
        return self.nodes.loc[nid]['y':'x']

    def get_nearest_nodes(self, lat, lon, return_dist=False):
        return ox.distance.nearest_nodes(self.G, X=lon, Y=lat, return_dist=return_dist)

    def generate_random_node(self):
        nid = np.random.choice(self.nodes.index)
        return nid

    def get_adjacent_node(self, nid, reverse=False):
        if not reverse:
            if self.dead_end:
                if nid not in self.edges.index.get_level_values('u'):
                    return []
            adjacent_lst = list(map(lambda x: x[-2], self.edges.loc[nid, :, :].index))
        else:
            if self.dead_end:
                if nid not in self.edges.index.get_level_values('v'):
                    return []
            adjacent_lst = list(map(lambda x: x[0], self.edges.loc[:, nid, :].index))

        return adjacent_lst

    def get_shortest_route(self, nid_from, nid_to, cpus=None):
        return ox.distance.shortest_path(self.G, nid_from, nid_to, weight='travel_time', cpus=cpus)

    def get_travel_time(self, route, reject_time=None, to_list=False):
        travel_time = [0]

        if reject_time:
            for i in range(len(route)-1):
                nid_from = route[i]
                nid_to = route[i+1]
                travel_time.append(int(self.edges.loc[(nid_from, nid_to, 0)]['travel_time'])+1)

                if sum(travel_time) >= reject_time:
                    return reject_time
        else:
            for i in range(len(route)-1):
                nid_from = route[i]
                nid_to = route[i+1]
                travel_time.append(int(self.edges.loc[(nid_from, nid_to, 0)]['travel_time'])+1)

        if to_list:
            return travel_time
        else:
            return sum(travel_time)

    def get_shortest_travel_time(self, nid_from, nid_to, return_route=False, to_list=False, reject_time=None):
        if self.shortest_paths:
            route = [nid_from]
            travel_time = [0]
            prev_nid = nid_from
            while prev_nid != nid_to:
                next_nid, time = self.shortest_paths[prev_nid][nid_to]
                route.append(next_nid)
                travel_time.append(time)
                prev_nid = next_nid
            if not to_list:
                travel_time = sum(travel_time)
        else:
            route = self.get_shortest_route(nid_from, nid_to)
            travel_time = self.get_travel_time(route, reject_time=reject_time, to_list=to_list)
        if return_route:
            return travel_time, route
        return travel_time

    def get_node_coordinate(self, nid):
        y, x = self.nodes.loc[nid, ['y', 'x']]
        return y, x

    def __remove_dead_end(self):
        print("remove dead end...", end="\t")
        start_nid = self.nodes.index[0]     # must not be dead end
        visited = {}
        dead_end = {}
        self.__dfs(start_nid, visited, dead_end, reverse=False)
        visited.clear()
        dead_end.clear()
        self.__dfs(start_nid, visited, dead_end, reverse=True)
        self.G = ox.utils_graph.graph_from_gdfs(self.nodes, self.edges)
        print("removed")

    def __dfs(self, nid, visited, dead_end, reverse=False):
        if nid in visited:
            if nid not in dead_end:
                # cycle
                dead_end[nid] = False
        else:
            visited[nid] = True
            adjacent_lst = self.get_adjacent_node(nid, reverse=reverse)

            if adjacent_lst:
                check_adj = []
                for adj_nid in adjacent_lst:
                    check_adj.append(self.__dfs(adj_nid, visited, dead_end, reverse=reverse))

                if False in check_adj:
                    dead_end[nid] = False
                    return dead_end[nid]

            self.nodes = self.nodes.drop(labels=nid, axis=0)

            if reverse:
                self.edges = self.edges.drop(labels=nid, level='u', axis=0)
            else:
                self.edges = self.edges.drop(labels=nid, level='v', axis=0)
            dead_end[nid] = True
            print("drop node", nid)

        return dead_end[nid]

    def save_network(self, filepath):
        ox.save_graphml(self.G, filepath)

    def __map(self):
        self.mapping = {}
        for i, node in enumerate(self.G.nodes):
            self.mapping[i] = node

    def plot_route(self, route):
        fig, ax = ox.plot_graph_route(self.G, route, orig_dest_size=200, route_color='g')
        plt.show()

"""
    def plot_nodes(self, *nodes):
        fig, ax = plt.subplots(figsize=(12, 8))
        for node in nodes:
            ox.plot_graph_route(self.G, [node], ax=ax)
        plt.show()
"""











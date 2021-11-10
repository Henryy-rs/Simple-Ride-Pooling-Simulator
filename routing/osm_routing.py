import networkx as nx
import osmnx as ox
import numpy as np
import sys

sys.setrecursionlimit(100000)


class OSMEngine:
    def __init__(self, dead_end=False):
        print("Initialize OSM Engine")
        self.G = ox.graph_from_place("Manhattan,New York USA", network_type="drive")
        self.G = ox.speed.add_edge_speeds(self.G)
        self.G = ox.speed.add_edge_travel_times(self.G)
        self.nodes, self.edges = ox.graph_to_gdfs(self.G)
        self.dead_end = True
        if not dead_end:
            self.__remove_dead_end()
            self.dead_end = False

    def get_location(self, nid):
        return self.nodes.loc[nid]['y':'x']

    def get_nearest_node(self, lat, lon):
        return ox.distance.nearest_nodes(self.G, X=lon, Y=lat)

    def generate_random_node(self):
        nid = np.random.choice(self.nodes.index)
        if self.dead_end:
            if nid not in self.edges.index:
                return self.generate_random_node()
        return nid

    def get_adjacent_node(self, nid, reverse=False):
        if not reverse:
            if self.dead_end:
                if nid not in self.edges.index.get_level_values('u'):
                    return []
            adjacent_lst = list(map(lambda x: x[1], self.edges.loc[nid, :, :].index))
        else:
            if self.dead_end:
                if nid not in self.edges.index.get_level_values('v'):
                    return []
            adjacent_lst = list(map(lambda x: x[0], self.edges.loc[:, nid, :].index))
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
        if self.dead_end:
            if route is None:
                print("NO ROUTE FROM {} TO {}".format(nid_from, nid_to))
                if reject_time:
                    return reject_time
                else:
                    if return_route:
                        return -1, []
                    else:
                        return -1
        travel_time = self.get_travel_time(route, reject_time=reject_time, to_list=to_list)
        if return_route:
            return travel_time, route
        return travel_time

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
        return dead_end[nid]

    def save_network(self):
        # todo: 모든 경로의 travel time 저장하여 속도 높이기
        return








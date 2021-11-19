from routing.osm_routing import OSMEngine
import pickle
import itertools

if __name__ == '__main__':
    engine = OSMEngine("data/Manhattan.graphml")
    n = len(engine.nodes.index)

    nodes = engine.nodes.index
    paths = {}
    for index, nid in enumerate(nodes):
        paths[index] = {}
        from_lst = [nid]*n
        routes = engine.get_shortest_route(from_lst, nodes, cpus=8)
        travel_times = []
        for i, route in enumerate(routes):
            travel_times.append(engine.get_travel_time(route, to_list=True))

        assert len(travel_times) == len(routes) == n, "error"

        for i in range(n):
            paths[index][i] = dict(route=routes[i], travel_time=travel_times[i])
        print("{}%".format(round(((index+1)/n)*100,2)))

    with open("data/paths/{}.pickle".format(index), "wb") as fw:
        pickle.dump(paths, fw)

    """
    from_lst = [[nid]*n for nid in engine.nodes.index]
    to_lst = [nid for nid in engine.nodes.index]*n

    print(len(from_lst))
    print(len(to_lst))

    print("find shortest paths...", end="\t")
    routes = engine.get_shortest_route(from_lst, to_lst, cpus=4)
    print("finished")

    nn = len(routes)
    travel_times = []

    print("get travel times...", end="\t")
    for index, route in enumerate(routes):
        travel_times.append(engine.get_travel_time(route, to_list=True))
        print("{}/{}".format(index, nn))
    print("finished")

    print("make dictionary...", end="\t")
    paths = {}
    for i in range(n):
        paths[i] = {}
        for j in range(n):
            paths[i][j] = dict(route=routes[i*n+j], travel_time=travel_times[i*n+j])
    print("finished")
    #print(len(paths))
    print("dump pickle")
    with open("shortest_paths.pickle", "wb") as fw:
        pickle.dump(paths, fw)
"""


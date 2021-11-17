from routing.osm_routing import OSMEngine
import pickle
import itertools

engine = OSMEngine("data/Manhattan.graphml")

n = len(engine.nodes.index)
from_lst = list(itertools.chain(*[[nid]*n for nid in engine.nodes.index]))
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
        paths[i][j] = dict(route=route[i*n+j], travel_time=travel_times[i*n+j])
print("finished")

print(len(paths))
print("dump pickle")
with open("paths.pickle", "wb") as fw:
    pickle.dump(paths, fw)


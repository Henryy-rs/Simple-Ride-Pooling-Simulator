from engine.osm import OSMEngine
import pickle
from collections import deque

if __name__ == '__main__':
    engine = OSMEngine("Manhattan.graphml")
    n = len(engine.nodes.index)
    paths = {}
    nodes = engine.nodes.index

    for nid in nodes:
        paths[nid] = {}
    for index, from_id in enumerate(nodes):
        from_ids = [from_id]*n
        to_ids = nodes
        routes = engine.get_shortest_route(from_ids, to_ids)
        travel_times = []

        for i, route in enumerate(routes):
            travel_times.append(engine.get_travel_time(route, to_list=True))

        to_id = 0
        for route, travel_time in zip(routes, travel_times):
            route = deque(route)
            travel_time = deque(travel_time)

            assert from_id == route.popleft() and travel_time.popleft() == 0, "error"

            prev_id = from_id

            while len(route) != 0:
                next_id = route.popleft()
                time = travel_time.popleft()

                if to_id not in paths[prev_id]:
                    paths[prev_id][to_id] = (next_id, time)
                else:
                    break

                prev_id = next_id

            if prev_id == to_id:
                paths[prev_id][to_id] = (to_id, 0)

            to_id += 1

        print("{}%".format(round(((index+1)/n)*100,2)))

    with open("paths.pickle", "wb") as f:
        pickle.dump(paths, f)

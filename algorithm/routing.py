import common.custom_tools as ct
from collections import deque


class Route:
    # event 는 노드에 도착했을 때 pop한다. 따라서 state가 1이나 2면 event는 항상 남아있어야 한다.
    # __time_left 는 변경하지 않아도 된다. travel deq 안의 첫 시간은 항상 0이다.
    def __init__(self):
        self.__route = deque()
        self.__travel_time = deque()
        self.__event = deque()

    def __len__(self):
        return len(self.__route)

    def push(self, route, route_tt, route_event):
        assert len(route) == len(route_tt) == len(route_event) != 0, \
            "invalid route expression. Length is different."
        self.__route = deque(route)
        self.__travel_time = deque(route_tt)
        self.__event = deque(route_event)
        self.pop_next()

    def pop_next(self):
        location = self.__route.popleft()
        time_left = self.__travel_time.popleft()
        return location, time_left

    def pop_event(self):
        return self.__event.popleft()


def find_min_candidate(candidate, v_nid, engine):
    r_id, r_state, origin, destination_ = candidate[0].values()
    if r_state == 1:
        travel_time, route = engine.get_shortest_travel_time(v_nid, origin, return_route=True, to_list=True)
    else:
        travel_time, route = engine.get_shortest_travel_time(v_nid, destination_, return_route=True, to_list=True)
    min_tt_lst = travel_time
    min_r_id = r_id
    min_route = route
    min_index = 0
    min_state = r_state

    for i in range(1, len(candidate)):
        r_id, r_state, origin, destination_ = candidate[i].values()

        if r_state == 1:
            travel_time, route = engine.get_shortest_travel_time(v_nid, origin, return_route=True, to_list=True)
        else:
            travel_time, route = engine.get_shortest_travel_time(v_nid, destination_, return_route=True,
                                                                    to_list=True)

        if sum(travel_time) < sum(min_tt_lst):
            min_tt_lst = travel_time
            min_r_id = r_id
            min_route = route
            min_index = i
            min_state = r_state

    if min_state == 1:
        candidate[min_index]['r_state'] += 1
    else:
        candidate.pop(min_index)

    return min_r_id, min_route, min_tt_lst


def plan_route(v_nid, time_left, timestep, candidate, route, tt_lst, event_lst, engine):
    min_r_id, min_route, min_tt_lst = find_min_candidate(candidate, v_nid, engine)
    route = ct.concate_route(route, min_route)
    tt_lst = ct.concate_tt_lst(tt_lst, min_tt_lst)
    event_lst = ct.mark_event(event_lst, min_r_id, len(min_route))
    v_nid = route[-1]     # next vehicle node id

    if sum(tt_lst) + time_left >= timestep:
        return route, tt_lst, event_lst
    else:
        if candidate:
            return plan_route(v_nid, time_left, timestep, candidate, route, tt_lst, event_lst, engine)
        else:
            return route, tt_lst, event_lst


def get_route(v_nid, v_time_left, timestep, candidate, engine):
    route_lst = [0]
    tt_lst = [0]
    event_lst = [-1]
    route_lst, tt_lst, event_lst = plan_route(v_nid, v_time_left, timestep, candidate, route_lst, tt_lst, event_lst, engine)
    route = Route()
    route.push(route_lst, tt_lst, event_lst)
    return route


def greedy_routing(vehicles, timestep, engine):
    for v_id, vehicle in vehicles.items():
        if vehicle.get_state() != 0:
            v_nid, v_time_left = vehicle.get_location()
            candidate = vehicle.get_candidests()
            vehicle.set_route(get_route(v_nid, v_time_left, timestep, candidate, engine))

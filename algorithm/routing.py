import common.custom_tools as ct
from collections import deque
from abc import *


class Route:
    def __init__(self):
        self.__route = deque()
        self.__travel_times = deque()
        self.__events = deque()

    def __len__(self):
        return len(self.__events)

    def push(self, route, route_tt, route_event):
        assert len(route) == len(route_tt) == len(route_event) != 0, "invalid route expression. Length is different."
        # event 는 노드에 도착했을 때 pop 한다. 따라서 state 가 1이나 2면 event 는 항상 남아있어야 한다.
        # __time_left 는 변경하지 않아도 된다. travel deq 안의 첫 시간은 항상 0이다.
        self.__route = deque(route)
        self.__travel_times = deque(route_tt)
        self.__events = deque(route_event)
        self.pop_next_location()

    def pop_next_location(self):
        location = self.__route.popleft()
        time_left = self.__travel_times.popleft()
        return location, time_left

    def pop_event(self):
        return self.__events.popleft()

    def get_split_route(self, v_node_id, v_time_left):
        if len(self) != 0:
            route = [v_node_id] + list(self.__route).copy()
            travel_times = [v_time_left] + list(self.__travel_times).copy()
            events = list(self.__events).copy()
            return route, travel_times, events
        else:
            raise Exception("No route to split. route is empty.")

    def print_event(self):
        print(self.__events)


class Router(metaclass=ABCMeta):
    def __init__(self, timestep, engine):
        self.timestep = timestep
        self.engine = engine

    @staticmethod
    def init_route():
        """
        init_route
        ===========

        :return: initial value of route, travel_times, events.
        Call this method before route planning.
        """
        return [0], [0], [[]]

    @staticmethod
    def concat_routes(route, travel_times, events, route_to_add, travel_times_to_add, request_id):
        route = ct.concat_routes(route, route_to_add)
        travel_times = ct.concat_travel_times(travel_times, travel_times_to_add)
        events = ct.mark_event(events, request_id, len(route_to_add))
        return route, travel_times, events

    @abstractmethod
    def set_vehicle_route(self, vehicle):
        pass

    @abstractmethod
    def plan_route(self):
        pass


class GreedyRouter(Router):
    def set_vehicle_route(self, vehicle):
        if vehicle.get_state() == 0:
            return
        route, travel_times, events = self.init_route()
        v_node_id, v_time_left = vehicle.get_location()
        candidates = vehicle.get_candidests()
        route, travel_times, events = self.plan_route(v_node_id, v_time_left, candidates, route, travel_times, events)
        combined_route = Route()
        combined_route.push(route, travel_times, events)
        vehicle.set_route(combined_route)

    def plan_route(self, v_node_id, v_time_left, candidates, route, travel_times, events):
        min_r_id, min_route, min_travel_times = self.find_min_candidate(candidates, v_node_id)
        route, travel_times, events = self.concat_routes(route, travel_times, events, min_route, min_travel_times,
                                                         min_r_id)
        v_node_id = route[-1]  # next vehicle node id

        if sum(travel_times) + v_time_left >= self.timestep:
            return route, travel_times, events
        else:
            if candidates:
                return self.plan_route(v_node_id, v_time_left, candidates, route, travel_times, events)
            else:
                return route, travel_times, events

    def find_min_candidate(self, candidates, v_node_id):
        r_id, r_state, origin, destination = candidates[0].values()
        if r_state == 1:
            travel_time, route = self.engine.get_shortest_travel_time(v_node_id, origin, return_route=True,
                                                                      to_list=True)
        else:
            travel_time, route = self.engine.get_shortest_travel_time(v_node_id, destination, return_route=True,
                                                                      to_list=True)
        min_travel_times = travel_time
        min_r_id = r_id
        min_route = route
        min_index = 0
        min_state = r_state

        for i in range(1, len(candidates)):
            r_id, r_state, origin, destination = candidates[i].values()

            if r_state == 1:
                travel_time, route = self.engine.get_shortest_travel_time(v_node_id, origin, return_route=True,
                                                                          to_list=True)
            else:
                travel_time, route = self.engine.get_shortest_travel_time(v_node_id, destination, return_route=True,
                                                                          to_list=True)

            if sum(travel_time) < sum(min_travel_times):
                min_travel_times = travel_time
                min_r_id = r_id
                min_route = route
                min_index = i
                min_state = r_state

        if min_state == 1:
            candidates[min_index]['r_state'] += 1
        else:
            candidates.pop(min_index)

        return min_r_id, min_route, min_travel_times


class InsertionRouter(Router):
    def set_vehicle_route(self, vehicle):
        if vehicle.get_state() == 0:
            return
        route, travel_times, events = self.plan_route(vehicle)
        # print("route:", route)
        # print("travel_time:", travel_times)
        # print("events: ", events)
        combined_route = Route()
        combined_route.push(route, travel_times, events)
        vehicle.set_route(combined_route)

    def plan_route(self, vehicle):
        v_node_id, v_time_left = vehicle.get_location()
        candidates = vehicle.get_candidests(only_new_requests=True)
        combined_route = vehicle.get_route()

        if len(combined_route) == 0:    # if this condition is True, Vehicle has no route plan.
            candidate = candidates.pop()
            origin = candidate['origin']
            destination = candidate['destination']
            request_id = candidate['r_id']
            assert origin != destination, "request error"

            # current vehicle's location -> origin -> destination
            route, travel_times, events = self.__concat_shortest_route(*self.init_route(), v_node_id, origin, request_id)
            route, travel_times, events = self.__concat_shortest_route(route, travel_times, events, origin, destination, request_id)
        else:
            route, travel_times, events = combined_route.get_split_route(v_node_id, v_time_left)

        for candidate in candidates:
            origin = candidate['origin']
            destination = candidate['destination']
            request_id = candidate['r_id']
            start_index = 0      # start_index: search from start_index

            # insert origin first.
            start_offset, end_offset = self.__find_best_place_to_insert(route, events, start_index=start_index,
                                                                        node_id_to_insert=destination)

            if not end_offset:
                # concat at the end (end_node -> origin -> destination)
                end_node_id = route[-1]
                route, travel_times, events = self.__concat_shortest_route(route, travel_times, events, end_node_id, origin, request_id)
                start_index = len(route) - 1

            elif start_offset == end_offset:
                # It means, no need to change route. Just append event in the current route.
                events[start_offset].append(request_id)
                start_index = start_offset

            else:
                from_node_id = route[start_offset]
                to_node_id = route[end_offset]

                route_to_insert, travel_times_to_insert, events_to_insert = \
                    self.__concat_shortest_route(*self.init_route(), from_node_id, origin, request_id)

                start_index = start_offset + len(route_to_insert) - 1   # index of origin

                route_to_insert, travel_times_to_insert, events_to_insert = \
                    self.__concat_shortest_route(route_to_insert, travel_times_to_insert, events_to_insert,
                                                 origin, to_node_id, events[end_offset])

                if end_offset == len(route) - 1:
                    route = route[:start_offset+1] + route_to_insert[1:]
                    travel_times = travel_times[:start_offset+1] + travel_times_to_insert[1:]
                    events = events[:start_offset+1] + events_to_insert[1:]
                else:
                    route = route[:start_offset+1] + route_to_insert[1:] + route[end_offset+1:]
                    travel_times = travel_times[:start_offset+1] + travel_times_to_insert[1:] + travel_times[end_offset+1:]
                    events = events[:start_offset+1] + events_to_insert[1:] + events[end_offset+1:]

            if request_id not in events[start_index]:
                print(request_id)
                print(events[start_index])
                print(events)
                raise Exception("invalid start_index")

            # insert destination
            start_offset, end_offset = self.__find_best_place_to_insert(route, travel_times, start_index=start_index,
                                                                        node_id_to_insert=destination)
            if not end_offset:
                # concat at the end (end_node -> origin -> destination)
                end_node_id = route[-1]
                route, travel_times, events = self.__concat_shortest_route(route, travel_times, events, end_node_id, destination, request_id)

            elif start_offset == end_offset:
                # It means, no need to change route. Just append event in the current route.
                events[start_offset].append(request_id)

            else:
                from_node_id = route[start_offset]
                to_node_id = route[end_offset]

                route_to_insert, travel_times_to_insert, events_to_insert = \
                    self.__concat_shortest_route(*self.init_route(), from_node_id, destination, request_id)

                assert events[end_offset] != []

                route_to_insert, travel_times_to_insert, events_to_insert = \
                    self.__concat_shortest_route(route_to_insert, travel_times_to_insert, events_to_insert,
                                                 destination, to_node_id, events[end_offset])

                if end_offset == len(route) - 1:
                    route = route[:start_offset+1] + route_to_insert[1:]
                    travel_times = travel_times[:start_offset+1] + travel_times_to_insert[1:]
                    events = events[:start_offset+1] + events_to_insert[1:]
                else:
                    route = route[:start_offset+1] + route_to_insert[1:] + route[end_offset+1:]
                    travel_times = travel_times[:start_offset+1] + travel_times_to_insert[1:] + travel_times[end_offset+1:]
                    events = events[:start_offset+1] + events_to_insert[1:] + events[end_offset+1:]

        return route, travel_times, events

    def __insert_request(self):
        return

    def __find_best_place_to_insert(self, route, events, start_index, node_id_to_insert):
        assert len(route) == len(events), "Invalid inputs."

        events_idx = []
        additional_times = []

        prev_offset = start_index
        prev_node_id = route[start_index]

        for i in range(start_index+1, len(events)):
            if events[i]:
                #print(events[i])
                events_idx.append(i)

        for offset in events_idx:
            additional_times.append([self.__get_additional_time(prev_node_id, node_id_to_insert, route[i]), prev_offset, offset])
            prev_node_id = route[offset]
            prev_offset = offset

        additional_times.append([self.__get_additional_time(prev_node_id, node_id_to_insert), prev_offset, None])

        min_additional_time = additional_times[0][0]
        min_start_offset = additional_times[0][1]
        min_end_offset = additional_times[0][2]

        for additional_time, start_offset, end_offset in additional_times:
            if additional_time < min_additional_time:
                min_additional_time = additional_time
                min_start_offset = start_offset
                min_end_offset = end_offset

        if min_additional_time == 0:
            min_end_offset = min_start_offset

        return min_start_offset, min_end_offset

    def __concat_shortest_route(self, route, travel_times, events, from_node_id, to_node_id, request_id):
        travel_times_to_add, route_to_add = self.engine.get_shortest_travel_time(from_node_id, to_node_id,
                                                                                 to_list=True, return_route=True)
        return self.concat_routes(route, travel_times, events, route_to_add, travel_times_to_add, request_id)

    def __get_additional_time(self, to_id, insert_id, from_id=None):
        time = 0
        if not from_id:
            time += self.engine.get_shortest_travel_time(to_id, insert_id)
        else:
            time += self.engine.get_shortest_travel_time(to_id, insert_id)
            time += self.engine.get_shortest_travel_time(insert_id, from_id)
            time -= self.engine.get_shortest_travel_time(to_id, from_id)

        return time

from collections import deque


class Route:
    def __init__(self):
        self.__route = deque()
        self.__route_travel_t = deque()
        self.__route_event = deque()

    def __len__(self):
        return len(self.__route)

    def push(self, route, route_tt, route_event):
        if not (len(route) == len(route_tt) == len(route_event) != 0):
            print(route, len(route))
            print(route_tt, len(route_tt))
            print(route_event, len(route_event))
            raise Exception("invalid route")
        self.__route = deque(route)
        self.__route_travel_t = deque(route_tt)
        self.__route_event = deque(route_event)
        self.pop_next()

    def pop_next(self):
        location = self.__route.popleft()
        time_left = self.__route_travel_t.popleft()
        return location, time_left

    def pop_event(self):
        return self.__route_event.popleft()

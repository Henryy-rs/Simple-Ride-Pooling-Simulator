from collections import deque
import numpy as np


class Route:
    def __init__(self):
        self.__route = deque()
        self.__travel_time = deque()
        self.__event = deque()

    def __len__(self):
        return len(self.__route)

    def push(self, route, route_tt, route_event):
        assert len(route) == len(route_tt) == len(route_event) != 0, \
            "invalid route expression. Length is different "
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


import numpy as np
from collections import deque

class Vehicle:
    max_capacity = 8

    def __init__(self, vid, engine):
        self.vid = vid
        self.location = engine.generate_random_node()
        # time_left until location
        self.time_left = 0
        self.requests = {}
        self.requests_state = {}
        """
        0: match(waiting)
        1: on ride
        """
        self.route = deque()
        self.route_travel_time = None
        self.cur_capacity = self.max_capacity
        self.state = 0
        self.history = []

        # history 조작할 때 destination을 체크해서 상태를 업데이트하자.
        """
        state
        0: emtpy
        1: occupied(or will be)
        2: full
        """
    def reset_location(self, engine):
        self.time_left = 0
        self.history = []
        self.location = engine.generate_random_node()
        #queue초기화 할지 말지 생각해봐야함 왜냐면 승객 태웠을 때 막다른 길에 갈 수도 있으니까

    def update_location(self, timestep, engine):
        if self.state == 0:
            if self.time_left > timestep:
                self.time_left -= timestep
            else:
                timestep -= self.time_left
                adjacent_lst = engine.get_adjacent_node(self.location)
                # if dead end
                if len(adjacent_lst) == 0:
                    self.reset_location(engine=engine)
                else:
                    adjacent = np.random.choice(adjacent_lst)
                    self.time_left = engine.get_travel_time([self.location, adjacent])
                    self.history.append(self.location)
                    self.location = adjacent
                    self.update_location(timestep, engine)
        elif self.state == 1:
            return
        elif self.state == 2:
            return
        return

    def print_history(self):
        print(self.history)

    def get_state(self):
        return self.state

    def get_location(self):
        return self.location, self.time_left

    def can_ride(self, n):
        if self.cur_capacity - n >= 0 and n >= 0 and type(n) == int:
            return True
        else:
            return False

    def ride(self, request, rid, n):
        self.requests[rid] = request
        self.requests_state[rid] = 0
        self.cur_capacity -= n
        if self.state == 0:
            self.state = 1
        elif self.state == 1:

    def set_route(self, route, time_left):
        self.
        self.location = self.route.get()
        self.time_left = time_left







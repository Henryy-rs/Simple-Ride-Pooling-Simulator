from logging import raiseExceptions
import numpy as np
from collections import deque
import requests


class Vehicle:
    max_capacity = 8

    def __init__(self, v_id, engine):
        self.v_id = v_id
        self.requests = {}

        # location expression
        self.location = engine.generate_random_node()
        self.time_left = 0

        # route expression
        self.route = deque()
        self.route_travel_time = deque()
        self.route_event = deque()

        self.history = []

        self.occupancy = 0
        self.state = 0

    def update_location(self, next_time, time_left, engine):
        """
        update_location
        ================

        Args:

            - next_time: float, start time of next step.
            - time_left: float, time remaining untill next step.
            - engine: OSMEngine, routing engine.
        """
        if self.time_left > time_left:
            self.time_left -= time_left
        else:
            if self.state == 0:
                time_left -= self.time_left
                adjacent_lst = engine.get_adjacent_node(self.location)

                if len(adjacent_lst) == 0:  # if dead end
                    self.reset_location(engine=engine)
                else:
                    adjacent = np.random.choice(adjacent_lst)
                    self.time_left = engine.get_travel_time([self.location, adjacent])
                    self.location = adjacent
                    self.update_location(next_time, time_left, engine)

            else:
                time_left -= self.time_left

                if len(self.route) != 0:
                    r_id = self.route_event.popleft()
                    # todo: 승객 시간 측정(performance measure)
                    if r_id != -1:  # nothing happens when we get to the node.
                        request = self.requests[r_id]
                        request.update_state()

                        if request.get_state() == 2: 
                            self.pick_up(r_id, next_time, time_left)
                        elif request.get_state() == 3:
                            self.drop_off(r_id, next_time, time_left)
                        else:
                            raise Exception("invalid request state.")

                    self.location = self.route.popleft()
                    self.time_left = self.route_travel_time.popleft()
                else:
                    raise Exception("asynchronous route planning.")

                self.update_location(next_time, time_left, engine)

    def print_history(self):
        print(self.history)

    def get_state(self):
        """        
        get_state
        ==========

        Returns:
            int:
                0: emtpy
                1: occupied(or will be)
                2: full
        """
        return self.state

    def get_location(self):
        return self.location, self.time_left

    def can_en_route(self, n):
        assert type(n) == int and n >= 0, "unexpected "

        if self.occupancy + n <= self.max_capacity:
            return True
        else:
            return False

    def en_route(self, request, r_id, n):
        r_state = request.get_state()
        assert r_state == 0, "state doesn't match"
        request.update_state()    # waiting state
        self.requests[r_id] = request
        self.occupancy += n
        if self.occupancy == self.max_capacity:
            self.state = 2
        elif self.state == 0:     # if vehicle is empty
            self.state = 1
        print("vehicle {} and user {} matched".format(self.v_id, r_id))

    def pick_up(self, r_id, next_time, time_left):
        self.history.append((r_id, next_time - time_left, self.requests[r_id].get_state(), self.location))
        print("vehicle {} pick up user {}".format(self.v_id, r_id))

    def drop_off(self, r_id, next_time, time_left):
        request = self.requests.pop(r_id)
        self.history.append((r_id, next_time - time_left, request.get_state(), self.location))
        self.occupancy -= request.get_n_customers()
        if self.occupancy == 0:
            self.state = 0
        print("vehicle {} drops off user {}".format(self.v_id, r_id))

    def set_plan(self, route, route_travel_time, route_event):
        self.route = deque(route)
        self.route_travel_time = deque(route_travel_time)
        self.route_event = deque(route_event)

        assert self.location == self.route.popleft(), "location doesn't match"
        assert self.route_travel_time.popleft() == 0, "invalid travel time list"
        assert len(self.route) == len(self.route_travel_time), "asynchronous"

        # event 는 도착하면 pop 할 것
        # time_left 는 건드릴 필요 없음

    # 현재 보유중인 request 상황을 참고하여 가능한 다음 목적지를 반환
    def get_candidate_destination(self):
        candidate_destination = []
        for rid, request in self.requests.items():
            r_state = request.get_state()

            assert r_state == 1 or 2

            if r_state == 1:
                candidate_destination.append((rid, request.get_origin()))
            else:
                candidate_destination.append((rid, request.get_destination()))
        return candidate_destination












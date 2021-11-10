import numpy as np
from collections import deque


class Vehicle:
    max_capacity = 8

    def __init__(self, v_id, engine):
        self.v_id = v_id
        self.location = engine.generate_random_node()
        # time_left until location
        self.time_left = 0
        self.requests = {}
        """
        0: match(waiting)
        1: on ride
        """
        self.route = deque()
        self.route_travel_time = deque()
        self.route_event = deque()

        self.occupancy = 0
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
        if self.time_left > timestep:
            self.time_left -= timestep
        else:
            if self.state == 0:
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
            else:
                timestep -= self.time_left
                self.history.append(self.location)
                if len(self.route) != 0:
                    self.location = self.route.popleft()
                    self.time_left = self.route_travel_time.popleft()
                    r_id = self.route_event.popleft()
                    # todo: 승객 시간 측정(performance measure)
                    if r_id != -1:
                        request = self.requests[r_id]
                        request.update_state()
                        if request.get_state() == 3:    # when arrived
                            self.drop_off(r_id)
                        else:
                            print("vehicle {} pick up user {}".format(self.v_id, r_id))
                else:
                    print(self.state)
                    print(self.route)
                    print(self.route_event)
                    print(self.route_travel_time)
                    raise Exception("asynchronous state")
                self.update_location(timestep, engine)

    def print_history(self):
        print(self.history)

    def get_state(self):
        return self.state

    def get_location(self):
        return self.location, self.time_left

    def can_pick_up(self, n):
        assert type(n) == int and n >= 0, "unexpected input"

        if self.occupancy + n <= self.max_capacity:
            return True
        else:
            return False

    def pick_up(self, request, r_id, n):
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

    def drop_off(self, r_id):
        self.occupancy -= self.requests.pop(r_id).get_n_customers()
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












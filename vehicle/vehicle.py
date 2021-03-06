import numpy as np
from algorithm.routing import Route


class Vehicle:
    __max_capacity = 6

    def __init__(self, v_id, engine):
        self.__v_id = v_id
        self.__requests = {}
        self.__new_requests = {}
        self.__serve_time = 0
        self.__history = []
        self.__n_serve_steps = 0

        # location expression
        self.__location = engine.generate_random_node()
        self.__time_left = 0

        # route expression
        self.__route = Route()

        # state expression
        self.__capacity = self.__max_capacity
        self.__occupancy = 0
        self.__state = 0

    def update_location(self, time_left, engine):
        """
        update_location
        ================
        update vehicle's location recursively
        
        Args:

            - next_time: float, start time of next step.
            - __time_left: float, time remaining until next step.
            - engine: OSMEngine, engine engine.
        """
        if self.__time_left >= time_left:
            if self.__occupancy != 0:
                self.__serve_time += time_left
            self.__time_left -= time_left
        else:
            if self.__state == 0:
                time_left -= self.__time_left
                adjacent_lst = engine.get_adjacent_node(self.__location)
                adjacent = np.random.choice(adjacent_lst)
                self.__time_left = engine.get_travel_time([self.__location, adjacent])
                self.__location = adjacent
                self.update_location(time_left, engine)
            else:
                time_left -= self.__time_left

                if self.__occupancy > 0:
                    self.__serve_time += self.__time_left

                events = self.__route.pop_event()

                for r_id in events:
                    self.__event(r_id, time_left)

                if self.__state != 0:
                    if time_left != 0:
                        self.__location, self.__time_left = self.__route.pop_next_location()
                    else:
                        self.__time_left = 0
                else:
                    self.__time_left = 0

                self.update_location(time_left, engine)

    def get_state(self):
        """        
        Vehicle State
        ==============

        Returns:
            int:
                0: emtpy
                1: occupied(or will be)
                2: full(or will be)
        """
        return self.__state

    def get_location(self):
        return self.__location, self.__time_left

    def is_rideable(self, request):
        n = len(request)    # number of passengers
        assert type(n) == int and n >= 0, "unexpected input."

        if self.__capacity - n >= 0:
            return True
        else:
            return False

    def join(self, request, time_left):
        r_state = request.get_state()
        r_id = request.get_id()

        assert r_state == 0, "__state doesn't match."

        request.update_state()    # waiting state

        self.__requests[r_id] = request
        self.__new_requests[r_id] = request
        self.__capacity -= len(request)

        if self.__capacity == 0:
            self.__state = 2
        elif self.__occupancy == 0:     # vehicle is empty but get passengers
            self.__state = 1

        self.__record(r_id, request.get_state(), time_left)
        # print("vehicle {} and user {} matched".format(self.__v_id, r_id))

    def __event(self, r_id, time_left):
        request = self.__requests[r_id]
        request.update_state()

        if request.get_state() == 2:
            self.__pick_up(r_id, time_left)
        elif request.get_state() == 3:
            self.__drop_off(r_id, time_left)
        else:
            raise Exception("invalid request state.")

    def __pick_up(self, r_id, time_left):
        self.__occupancy += len(self.__requests[r_id])
        self.__record(r_id, self.__requests[r_id].get_state(), time_left)
        # print("vehicle {} picks up user {}".format(self.__v_id, r_id))

    def __drop_off(self, r_id, time_left):
        request = self.__requests.pop(r_id)
        self.__occupancy -= len(request)
        self.__capacity += len(request)

        if self.__capacity == self.__max_capacity:
            self.__state = 0

        self.__record(r_id, request.get_state(), time_left)
        # print("vehicle {} drops off user {}".format(self.__v_id, r_id))

    def set_route(self, route):
        self.__route = route
        self.__new_requests = {}

    def get_route(self):
        return self.__route

    # ?????? ???????????? request ????????? ???????????? ????????? ?????? ???????????? ??????
    def get_candidests(self, only_new_requests=False):
        """
        get_candidests
        ===============

        return candidate destinations.
        """
        candidate_destination = []

        if only_new_requests:
            requests = self.__new_requests
        else:
            requests = self.__requests

        for r_id, request in requests.items():
            r_state = request.get_state()

            assert r_state == 1 or 2

            candidate_destination.append({'r_id': r_id, 'r_state': r_state, 'origin': request.get_origin(),
                                          'destination': request.get_destination()})

        return candidate_destination

    def get_id(self):
        return self.__v_id

    def __record(self, r_id, r_state, time_left):
        self.__history.append({'v_id': self.__v_id, 'r_id': r_id, 'r_state': r_state,
                               'time': int(time_left), 'location': self.__location})
   
    def send_event_history(self):
        history = self.__history.copy()
        self.__history.clear()
        return history

    def send_vehicle_history(self):
        serve_time = self.__serve_time
        self.__serve_time = 0
        occupancy_rate = self.__occupancy/self.__max_capacity
        return serve_time, occupancy_rate

    def update_serve_steps(self):
        self.__n_serve_steps += 1

    def get_n_serve_steps(self):
        return self.__n_serve_steps

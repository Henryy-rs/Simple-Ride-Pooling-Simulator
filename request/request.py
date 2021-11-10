class Request:
    # 조건에 따라 달라지게 할 수 있음
    reject_time = 60*15

    def __init__(self, rid, best_trip_time, origin, destination):
        self.id = rid
        self.best_trip_time = best_trip_time
        self.origin = origin
        self.destination = destination
        self.waiting_time = 0
        self.state = 0
        self.n_customers = 1
        """
        state
        0: not assigned
        1: waiting(assigned)
        2: moving
        3: arrived
        """
        self.route = None

    def get_origin(self):
        return self.origin

    def get_destination(self):
        return self.destination

    def get_reject_time(self):
        return self.reject_time

    def get_rid(self):
        return self.id

    def get_n_customers(self):
        return self.n_customers

    def get_state(self):
        return self.state
    """
    def set_state(self, state):
        self.state = state
    """
    def update_state(self):
        self.state += 1




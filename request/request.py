class Request:
    reject_time = 60*15

    def __init__(self, rid, best_trip_time, origin, destination):
        self.id = rid
        self.best_trip_time = best_trip_time
        self.origin = origin
        self.destination = destination
        self.waiting_time = 0
        self.state = 0
        self.n = 1
        self.route = None

    def get_origin(self):
        return self.origin

    def get_destination(self):
        return self.destination

    def get_reject_time(self):
        return self.reject_time

    def get_id(self):
        return self.id

    def __len__(self):
        return self.n

    def get_state(self):
        """        
        Request State
        ==============

        Returns:
            int:
                0: not assigned
                1: waiting vehicle
                2: on board
                3: arrived
        """
        return self.state

    def update_state(self):
        self.state += 1

    def get_best_tt(self):
        return self.best_trip_time

    def log_info(self):
        print("r_id: {}, origin: {}, destination: {}".format(self.id, self.origin, self.destination))




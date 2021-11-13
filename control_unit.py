from routing.osm_routing import OSMEngine
from vehicle.vehicle import Vehicle
from algorithm import matcing_policy
from request.request_loader import RequestLoader
from record.recorder import Recorder

class ControlUnit:
    def __init__(self, start, timestep, n_vehicles, matching_method, keys, db_dir, save_dir):
        self.start = start
        self.timestep = timestep
        self.current_time = 0
        self.n_vehicles = n_vehicles
        self.matching_method = matching_method
        self.vehicles = {}
        self.requests = {}
        self.r_ids_add = []
        self.engine = OSMEngine()
        self.request_loader = RequestLoader(db_dir=db_dir)
        self.recorder = Recorder(keys=keys, save_dir=save_dir)

    def dispatch_vehicles(self):
        print("dispatch...", end="\t")
        self.vehicles = {}

        for v_id in range(self.n_vehicles):
            self.vehicles[v_id] = Vehicle(v_id=v_id, engine=self.engine)

        print("finished")

    def step(self, current_time):
        self.current_time = current_time
        requests = self.request_loader.iter_request(self.current_time, self.timestep, engine=self.engine)
        self.__match(requests)
        self.__update_vehicles_locations()
        self.__gather_records()
        print("matched: ", self.__get_n_matched())
        self.__add_requests(requests)

    def __update_vehicles_locations(self):
        print("update location...")

        for vehicle in self.vehicles.values():
            vehicle.update_location(time_left=self.timestep, engine=self.engine)
        print("finished")

    def __match(self, requests):
        if self.matching_method == "greedy":
            matcing_policy.greedy_matching(requests, self.vehicles, self.timestep, engine=self.engine)

    def __gather_records(self):
        for v_id, vehicle in self.vehicles.items():
            for record in vehicle.send_event_history():
                self.recorder.put_event(record, next_time=self.current_time + self.timestep, control_unit=self)

            self.recorder.put_v_metrics(v_id, vehicle.send_vehicle_history())
            
    def manage_request(self, r_id):
        self.r_ids_add.append(r_id)

    def release_request(self, r_id):
        return self.requests.pop(r_id)

    def __get_n_matched(self):
        return len(self.r_ids_add)

    def __add_requests(self, requests):
        for r_id in self.r_ids_add:
            self.requests[r_id] = requests[r_id]
        self.r_ids_add.clear()






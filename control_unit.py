from routing.osm_routing import OSMEngine
from vehicle.vehicle import Vehicle
from algorithm import matcing_policy
from request.request_loader import RequestLoader
from record.recorder import Recorder

class ControlUnit:
    def __init__(self, current_time, timestep, n_vehicles, matching_method, keys, db_dir, save_dir):
        self.timestep = timestep
        self.current_time = current_time
        self.current_step = 1
        self.n_vehicles = n_vehicles
        self.matching_method = matching_method
        self.vehicles = {}
        self.requests = {}
        self.r_ids_to_add = []
        self.engine = OSMEngine()
        self.request_loader = RequestLoader(db_dir=db_dir)
        self.recorder = Recorder(keys=keys, save_dir=save_dir)

    def dispatch_vehicles(self):
        print("dispatch...", end="\t")
        self.vehicles = {}

        for v_id in range(self.n_vehicles):
            self.vehicles[v_id] = Vehicle(v_id=v_id, engine=self.engine)

        print("finished")

    def step(self):
        requests = self.request_loader.iter_request(self.current_time, self.timestep, engine=self.engine)
        self.__match(requests)
        self.__update_vehicles_locations()
        self.__gather_records(requests)
        self.current_time += self.timestep
        self.current_step += 1

    def __update_vehicles_locations(self):
        print("update location...")

        for vehicle in self.vehicles.values():
            vehicle.update_location(time_left=self.timestep, engine=self.engine)
        print("finished")

    def __match(self, requests):
        if self.matching_method == "greedy":
            matcing_policy.greedy_matching(requests, self.vehicles, self.timestep, engine=self.engine)

    def __gather_records(self, requests):
        for v_id, vehicle in self.vehicles.items():
            for record in vehicle.send_event_history():
                self.recorder.put_event(record, next_time=self.current_time + self.timestep, control_unit=self)

            serve_time, occupancy_rate = vehicle.send_vehicle_history()
            # TODO: add travel distance
            self.recorder.put_metrics(step=self.current_step, v_id=v_id, serve_time=serve_time, occunpancy_rate=occupancy_rate)

        accept_rate = self.__get_n_matched()/len(requests)
        # TODO: add throughput
        self.recorder.put_metrics(vehicles=False, step=self.current_step, accept_rate=accept_rate)
        self.__drop_requests(requests)
            
    def manage_request(self, r_id):
        self.r_ids_to_add.append(r_id)

    def release_request(self, r_id):
        return self.requests.pop(r_id)

    def __get_n_matched(self):
        return len(self.r_ids_to_add)

    def __drop_requests(self, requests):
        for r_id in self.r_ids_to_add:
            self.requests[r_id] = requests[r_id]
        self.r_ids_to_add.clear()






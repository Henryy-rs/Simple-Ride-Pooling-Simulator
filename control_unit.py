from engine.osm import OSMEngine
from vehicle.vehicle import Vehicle
from algorithm.routing import *
from algorithm.matcing import *
from request.request_loader import RequestLoader
from record.recorder import Recorder


class ControlUnit:
    def __init__(self, current_time, timestep, n_vehicles, matching_method, routing_method, db_dir,
                 test_mode=False, logging_mode=False, network_path=None, paths=""):
        self.test_mode = test_mode
        self.timestep = timestep
        self.current_time = current_time
        self.current_step = 1
        self.throughput = 0
        self.n_vehicles = n_vehicles
        self.vehicles = {}
        self.requests = {}
        self.step_requests = {}
        self.step_r_ids_accepted = []
        self.engine = OSMEngine(network_path=network_path, paths=paths)
        self.request_loader = RequestLoader(db_dir=db_dir, logging_mode=logging_mode)
        self.recorder = Recorder()
        self.matching_method = matching_method
        self.routing_method = routing_method
        self.__generate_commander()

    def __generate_commander(self):
        if self.matching_method == "greedy":
            self.matcher = GreedyMatcher(self.timestep, self.engine)
        elif self.matching_method == "angle":
            self.matcher = AngleMatcher(self.timestep, self.engine)
        elif self.matching_method == "rsubgraph":
            self.matcher = RestrictedSubgraphMatcher(self.timestep, self.engine)

        if self.routing_method == "greedy":
            self.router = GreedyRouter(self.timestep, self.engine)
        elif self.routing_method == "insertion":
            self.router = InsertionRouter(self.timestep, self.engine)
        else:
            raise Exception("There is no routing method '{}'".format(self.matching_method))

    def dispatch_vehicles(self):
        print("dispatch...", end="\t")
        self.vehicles = {}

        for v_id in range(self.n_vehicles):
            self.vehicles[v_id] = Vehicle(v_id=v_id, engine=self.engine)

        print("finished")

    def step(self):
        self.step_requests = self.request_loader.iter_request(self.current_time, self.timestep)
        self.__match(self.step_requests)
        self.__route()
        self.__update_vehicles_locations()
        self.__gather_records(self.step_requests)
        self.__ready_next_step()

    def __update_vehicles_locations(self):
        print("update location...")

        for vehicle in self.vehicles.values():
            vehicle.update_location(time_left=self.timestep, engine=self.engine)
        print("finished")

    def __match(self, requests):
        self.matcher.match(requests, self.vehicles)

    def __route(self):
        for vehicle in self.vehicles.values():
            self.router.set_vehicle_route(vehicle)

    def __gather_records(self, requests):
        for v_id, vehicle in self.vehicles.items():
            records = vehicle.send_event_history()
            self.recorder.put_events(records, next_time=self.current_time + self.timestep, control_unit=self)
            serve_time, occupancy_rate = vehicle.send_vehicle_history()
            # TODO: add travel distance
            self.recorder.put_metrics(self.current_step, v_id=v_id, serve_time=serve_time, occupancy_rate=occupancy_rate)

        accept_rate = self.__get_n_matched()/len(requests)
        self.recorder.put_metrics(self.current_step, vehicles=False, accept_rate=accept_rate, throughput=self.throughput)
        self.__filter_requests(requests)
            
    def manage_request(self, r_id):
        self.step_r_ids_accepted.append(r_id)

    def release_request(self, r_id):
        self.throughput += 1
        if r_id in self.requests:
            return self.requests.pop(r_id)
        else:
            self.step_r_ids_accepted.remove(r_id)
            return self.step_requests[r_id]

    def __get_n_matched(self):
        return len(self.step_r_ids_accepted)

    def __filter_requests(self, requests):
        for r_id in self.step_r_ids_accepted:
            self.requests[r_id] = requests[r_id]
        self.step_r_ids_accepted.clear()

    def __ready_next_step(self):
        self.current_time += self.timestep
        self.current_step += 1
        self.throughput = 0

    def print_result(self, save_dir):
        title = "{}+{}, n_vehicles={}".format(self.matching_method, self.routing_method, self.n_vehicles)
        self.recorder.print(title, save_dir)






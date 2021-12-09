from engine.osm import OSMEngine
from vehicle.vehicle import Vehicle
from algorithm.routing import *
from algorithm.matcing import *
from request.request_loader import RequestLoader
from record.recorder import Recorder
from collections import deque


class ControlUnit:
    def __init__(self, current_time, timestep, n_vehicles, matching_method, routing_method, db_dir,
                 test_mode=False, logging_mode=False, network_path=None, quantity_supplied="oversupply", paths=""):
        self.test_mode = test_mode
        self.timestep = timestep
        self.current_time = current_time
        self.current_step = 1
        self.throughput = 0
        self.n_vehicles = n_vehicles
        self.vehicles = {}
        self.requests = {}

        # used to adjust number of vehicles according to the number of requests.
        self.quantity_supplied = quantity_supplied
        if self.quantity_supplied:
            self.EMA = 20
            self.alpha = 0.5
            # queue
            self.sleeping_vehicles = deque()
            # arbitrarily set values. You can change them.
            if self.quantity_supplied == "over":
                self.k = 5
            elif self.quantity_supplied == "balanced":
                self.k = 3.5
            elif self.quantity_supplied == "under":
                self.k = 2

        self.step_requests = {}
        self.step_r_ids_accepted = []
        self.engine = OSMEngine(network_path=network_path, paths=paths)
        self.request_loader = RequestLoader(db_dir=db_dir)
        self.recorder = Recorder(logging_mode=logging_mode)
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
        if self.quantity_supplied:
            self.__adjust_n_vehicles()
        self.__match()
        self.__route()
        self.__update_vehicles_locations()
        self.__gather_records(self.step_requests)
        self.__ready_next_step()

    def __update_vehicles_locations(self):
        print("update location...")

        for vehicle in self.vehicles.values():
            vehicle.update_location(time_left=self.timestep, engine=self.engine)
            vehicle.update_serve_steps()
        print("finished")

    def __match(self):
        self.matcher.match(self.step_requests, self.vehicles)

    def __route(self):
        for vehicle in self.vehicles.values():
            self.router.set_vehicle_route(vehicle)

    def __gather_records(self, requests):
        for v_id, vehicle in self.vehicles.items():
            records = vehicle.send_event_history()
            self.recorder.put_events(records, next_time=self.current_time + self.timestep, control_unit=self)
            serve_time, occupancy_rate = vehicle.send_vehicle_history()
            # TODO: add travel distance
            self.recorder.put_metrics(vehicle.get_n_serve_steps(), v_id=v_id, serve_time=serve_time, occupancy_rate=occupancy_rate)
        accept_rate = self.__get_n_matched()/len(requests)
        utilization = len(self.vehicles)/self.n_vehicles
        self.recorder.put_metrics(self.current_step, vehicles=False, accept_rate=accept_rate,
                                  throughput=self.throughput, utilization=utilization)
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

    def __adjust_n_vehicles(self):
        n_requests = len(self.step_requests)
        self.EMA = self.alpha*n_requests + self.EMA*(1 - self.alpha)
        target_n_vehicles = int(self.EMA*self.k)
        active_n_vehicles = len(self.vehicles)
        delta = target_n_vehicles - active_n_vehicles

        if delta > 0:
            while delta > 0 and self.sleeping_vehicles:
                vehicle = self.sleeping_vehicles.popleft()
                v_id = vehicle.get_id()
                assert v_id not in self.vehicles.keys(), "management error"
                assert vehicle.get_state() == 0, "invalid vehicle's state"
                self.vehicles[v_id] = vehicle
                delta -= 1
        elif delta < 0:
            v_id_to_pop = []
            for v_id, vehicle in self.vehicles.items():
                if vehicle.get_state() == 0:
                    v_id_to_pop.append(v_id)
                    self.sleeping_vehicles.append(vehicle)
                    delta += 1
                    if delta == 0:
                        break
            for v_id in v_id_to_pop:
                self.vehicles.pop(v_id)

    def print_result(self, save_dir):
        if self.test_mode:
            title = "{}+{}, test_mode".format(self.matching_method, self.routing_method)
        else:
            title = "{}+{}, supply={}".format(self.matching_method, self.routing_method, self.quantity_supplied)
        self.recorder.print(title, save_dir, self.timestep)






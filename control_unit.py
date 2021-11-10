from routing.osm_routing import OSMEngine
from vehicle.vehicle import Vehicle
from algorithm import matcing_policy
from request.request_loader import RequestLoader


class ControlUnit:
    def __init__(self, start, timestep, n_vehicles, matching_method, db_dir, dead_end=False):
        self.start = start
        self.timestep = timestep
        self.n_vehicles = n_vehicles
        self.matching_method = matching_method
        self.vehicles = {}
        self.engine = OSMEngine()
        self.request_loader = RequestLoader(db_dir=db_dir, dead_end=dead_end)

    def dispatch_vehicles(self):
        print("dispatch...", end="\t")
        self.vehicles = {}
        for v_id in range(self.n_vehicles):
            self.vehicles[v_id] = Vehicle(v_id=v_id, engine=self.engine)
        print("finished")
        return self.vehicles

    def step(self, current_time):
        # load request data
        # 일단 멤버 변수로 저장하지 않겠음.
        requests = self.request_loader.iter_request(current_time=current_time, timestep=self.timestep, engine=self.engine)
        self.match(requests)
        # update vehicles location
        self.update_vehicles_locations()

    def update_vehicles_locations(self):
        print("update location...")
        # print(len(self.vehicles))
        for v_id, vehicle in self.vehicles.items():
            vehicle.update_location(timestep=self.timestep, engine=self.engine)
        print("finished")

    def match(self, requests):
        if self.matching_method == "greedy":
            matcing_policy.greedy_matching(requests, self.vehicles, self.timestep, engine=self.engine)







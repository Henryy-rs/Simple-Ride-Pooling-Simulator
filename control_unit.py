from routing.osm_routing import OSMEngine
from vehicle.vehicle import Vehicle
from algorithm import matcing_policy


class ControlUnit:
    def __init__(self, start, timestep, n_vehicles, matching_method):
        self.start = start
        self.timestep = timestep
        self.n_vehicles = n_vehicles
        self.matching_method = matching_method
        self.vehicles = []
        self.engine = OSMEngine()

    def dispatch_vehicles(self):
        print("dispatching...")
        for vid in range(self.n_vehicles):
            self.vehicles.append(Vehicle(vid=vid, engine=self.engine))
        return self.vehicles

    def update_vehicles_locations(self):
        for vehicle in self.vehicles:
            vehicle.update_location(timestep=self.timestep, engine=self.engine)

    def match(self, requests):
        if self.matching_method == "greedy":
            matcing_policy.greedy_matching(requests, self.vehicles, engine=self.engine)







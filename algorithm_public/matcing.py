import numpy as np
from math import pi
from abc import *
from common import geo_utils


class Matcher(metaclass=ABCMeta):
    def __init__(self, timestep, engine):
        self.timestep = timestep
        self.engine = engine

    @abstractmethod
    def match(self):
        pass


class GreedyMatcher(Matcher):
    def match(self, requests, vehicles):
        for request in requests.values():
            r_nid = request.get_origin()
            reject_time = request.get_reject_time()

            min_travel_time = reject_time
            min_v_id = -1

            for v_id, vehicle in vehicles.items():
                if vehicle.is_rideable(request):
                    # location heading and time left
                    v_nid, v_time_left = vehicle.get_location()
                    travel_time = self.engine.get_shortest_travel_time(v_nid, r_nid, reject_time=reject_time) + v_time_left
                    if travel_time < min_travel_time:
                        min_travel_time = travel_time
                        min_v_id = v_id

            if min_v_id != -1:
                vehicles[min_v_id].join(request, time_left=self.timestep)
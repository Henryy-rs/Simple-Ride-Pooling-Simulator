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


class RadianMatcher(Matcher):
    accept_range = 500
    accept_radian = pi/4
    k = 2
    base_distance = k * accept_range * np.sin(accept_radian)

    def match(self, requests, vehicles):
        for v_id, vehicle in vehicles.items():
            v_nid, v_time_left = vehicle.get_location()
            v_lat, v_lon = self.engine.get_latlon(v_nid)

            for r_id, request in requests.items():
                if request.get_state() != 0 or not vehicle.is_rideable(request):
                    continue

                o_lat, o_lon = self.engine.get_latlon(request.get_origin())
                distance = geo_utils.great_circle_distance(v_lat, v_lon, o_lat, o_lon)

                if distance > self.accept_range:
                    continue

                # if no customer match with vehicle
                if vehicle.get_state() == 0:
                    vehicle.join(request, self.timestep)
                else:
                    candidates = vehicle.get_candidests()
                    sum_d_lat = 0
                    sum_d_lon = 0

                    for candidate in candidates:
                        d_lat, d_lon = self.engine.get_latlon(candidate['destination'])
                        sum_d_lat += d_lat
                        sum_d_lon += d_lon

                    mean_d_lat = sum_d_lat / len(candidates)
                    mean_d_lon = sum_d_lon / len(candidates)

                    base_direction = geo_utils.bearing(v_lat, v_lon, mean_d_lat, mean_d_lon)

                    d_lat, d_lon = self.engine.get_latlon(request.get_destination())
                    r_direction = geo_utils.bearing(v_lat, v_lon, d_lat, d_lon)
                    delta = abs(base_direction - r_direction)

                    if self.accept_radian > delta:
                        distance = geo_utils.great_circle_distance(v_lat, v_lon, d_lat, d_lon)
                        distance *= np.sin(delta)

                        if self.base_distance > distance:
                            vehicle.join(request, self.timestep)

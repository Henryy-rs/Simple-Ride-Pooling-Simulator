import sqlite3
import pandas as pd
from request.request import Request


class RequestLoader:
    def __init__(self, db_dir):
        self.con = sqlite3.connect(db_dir)
        self.cur = self.con.cursor()
        self.requests = {}

    def iter_request(self, current_time, timestep, engine):
        print("load data...", end="\t")
        df = pd.DataFrame(self.cur.execute("SELECT id, request_datetime, trip_time, origin_lon, origin_lat, destination_lon, destination_lat"
                                           "  FROM request_backlog WHERE request_datetime >= (?) and request_datetime < (?)",
                                [current_time-timestep, current_time]).fetchall(),
                          columns=['id', 'datetime', 'trip_time', 'O_lon', 'O_lat', 'D_lon', 'D_lat'])
        requests = {}
        n_invalid = 0
        for index, (rid, datetime, trip_time, O_lon, O_lat, D_lon, D_lat) in df.iterrows():
            # nearest node from request (assume that pick up customer there)
            rid = int(rid)
            origin = engine.get_nearest_node(lat=O_lat, lon=O_lon)
            destination = engine.get_nearest_node(lat=D_lat, lon=D_lon)
            best_trip_time = engine.get_shortest_travel_time(origin, destination)
            if best_trip_time <= 0:   # destination == origin or no route
                n_invalid += 1
                continue
            requests[rid] = Request(rid, best_trip_time, origin, destination)
        print("{} requests loaded, {} are invalid".format(len(requests), n_invalid))
        self.requests = requests
        return self.requests


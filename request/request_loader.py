import sqlite3
import pandas as pd
from request.request import Request


class RequestLoader:
    def __init__(self, db_dir, write_db_mode=False):
        self.con = sqlite3.connect(db_dir)
        self.cur = self.con.cursor()
        self.write_db_mode = write_db_mode
        if self.write_db_mode:
            self.con_writer = sqlite3.connect("data/new_db.sqlite3")
            self.writer = self.con_writer.cursor()
            self.writer.execute("CREATE TABLE requests (id INTEGER, best_trip_time integer, origin INTEGER, destination INTEGER, datetime INTEGER)")

    def iter_request(self, current_time, timestep, engine):
        print("load data...", end="\t")
        df = pd.DataFrame(self.cur.execute("SELECT id, request_datetime, trip_time, origin_lon, origin_lat, destination_lon, destination_lat"
                                           "  FROM request_backlog WHERE request_datetime >= (?) and request_datetime < (?)",
                                           [current_time-timestep, current_time]).fetchall(),
                          columns=['id', 'datetime', 'trip_time', 'o_lon', 'o_lat', 'd_lon', 'd_lat'])
        requests = {}
        n_invalid = 0
        o_lat = df['o_lat']
        o_lon = df['o_lon']
        d_lat = df['d_lat']
        d_lon = df['d_lon']
        r_datetime = df['datetime']
        ids = list(map(lambda x: int(x), df['id']))
        origins, o_distances = engine.get_nearest_nodes(lat=o_lat, lon=o_lon, return_dist=True)
        destinations, d_distances = engine.get_nearest_nodes(lat=d_lat, lon=d_lon, return_dist=True)

        for i in range(len(df)):
            if o_distances[i] < 500 and d_distances[i] < 500 and origins[i] != destinations[i]:
                best_trip_time = engine.get_shortest_travel_time(origins[i], destinations[i])
                requests[ids[i]] = Request(ids[i], best_trip_time, origins[i], destinations[i])
                if self.write_db_mode:
                    self.writer.execute("INSERT INTO requests VALUES ({}, {}, {}, {}, {})".format(ids[i], best_trip_time, origins[i], destinations[i], r_datetime[i]))
            else:
                n_invalid += 1

        self.con_writer.commit()
        print("{} requests loaded, {} are invalid".format(len(requests), n_invalid))
        return requests


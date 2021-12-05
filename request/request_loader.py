import sqlite3
import pandas as pd
from request.request import Request


class RequestLoader:
    def __init__(self, db_dir):
        self.con = sqlite3.connect(db_dir)
        self.cur = self.con.cursor()

    def iter_request(self, current_time, timestep):
        print("load data...", end="\t")
        df = pd.DataFrame(self.cur.execute("SELECT id, best_trip_time, origin, destination"
                                           "  FROM requests WHERE datetime >= (?) and datetime < (?)",
                                           [current_time-timestep, current_time]).fetchall(),
                          columns=['id', 'best_trip_time', 'origin', 'destination'])
        requests = {}

        ids = list(map(lambda x: int(x), df['id']))
        best_trip_times = df['best_trip_time']
        origins = df['origin']
        destinations = df['destination']

        for i in range(len(df)):
            requests[ids[i]] = Request(ids[i], best_trip_times[i], origins[i], destinations[i])

        print("{} requests loaded".format(len(requests)))
        return requests


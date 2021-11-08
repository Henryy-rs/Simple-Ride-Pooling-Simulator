import sqlite3
import pandas as pd
from request.request import Request


class RequestLoader:
    def __init__(self, db_dir):
        self.con = sqlite3.connect(db_dir)
        self.cur = self.con.cursor()

    def iter_request(self, current_time, timestep):
        df = pd.DataFrame(self.cur.execute("SELECT id, request_datetime, trip_time, origin_lon, origin_lat, destination_lon, destination_lat"
                                           "  FROM request_backlog WHERE request_datetime >= (?) and request_datetime < (?)",
                                [current_time-timestep, current_time]).fetchall(),
                          columns=['id', 'datetime', 'trip_time', 'O_lon', 'O_lat', 'D_lon', 'D_lat'])
        request_lst = []
        for index, (rid, datetime, trip_time, O_lon, O_lat, D_lon, D_lat) in df.iterrows():
            origin = (O_lon, O_lat)
            destination = (D_lon, D_lat)
            request_lst.append(Request(rid, trip_time, origin, destination))
        return request_lst


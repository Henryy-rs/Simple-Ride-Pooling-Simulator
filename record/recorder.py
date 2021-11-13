import pandas as pd

from vehicle.vehicle import Vehicle


class Recorder:
    def __init__(self, keys, save_dir):
        self.df = pd.DataFrame(columns=keys)
        self.df = self.df.set_index(['v_id', 'r_id', 'r_state'])
        self.requests_to_record = [] 
        self.save_dir=save_dir
        vehicle_metrics = None
        system_metrics = None

        return

    def put_event(self, record, next_time, control_unit):
        # print("record: ", record)
        r_state = record['r_state']
        r_id = record['r_id']
        record['time_left'] = next_time - record['time_left']
        self.df.append(record, ignore_index=True)

        if r_state == 1:
            control_unit.manage_request(r_id)
        elif r_state == 3:
            request = control_unit.release_request(r_id)
            self.requests_to_record.append(request)

    def put_metrics(**kwargs):
        return

    def record_requests(self):
        return

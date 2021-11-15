from networkx.generators.community import LFR_benchmark_graph
import pandas as pd
from vehicle.vehicle import Vehicle


class Recorder:
    def __init__(self, save_dir):
        self.df = pd.DataFrame()
        self.r_df = pd.DataFrame() 
        self.v_df = pd.DataFrame(dtype=float)
        self.sys_metrics = {}
        self.requests_to_record = [] 
        self.save_dir=save_dir

    def put_events(self, records, next_time, control_unit):
        if records:
            tmp_df = pd.DataFrame(columns=list(records[0].keys()))
            tmp_df = tmp_df.astype(dict_v2type(records[0]))
        
            for record in records:
                r_state = record['r_state']
                r_id = record['r_id']
                record['time'] = next_time - record['time']
                tmp_df = tmp_df.append(record, ignore_index=True)

                if r_state == 1:
                    control_unit.manage_request(r_id)
                elif r_state == 3:
                    request = control_unit.release_request(r_id)
                    self.requests_to_record.append(request)
            
            tmp_df = tmp_df.set_index(['v_id', 'r_id', 'r_state'])
            self.df = pd.concat([self.df, tmp_df], axis=0)

    def put_metrics(self, step, vehicles=True, **kwargs):
        if vehicles:
            if step == 1:
                tmp_df = pd.DataFrame(columns=list(kwargs.keys()))
                tmp_df = tmp_df.append(kwargs, ignore_index=True)
                tmp_df = tmp_df.astype(dict_v2type(kwargs))
                tmp_df = tmp_df.set_index('v_id')
                self.v_df = pd.concat([self.v_df, tmp_df], axis=0)
            else:
                r_id = kwargs['v_id']
                series = pd.Series(kwargs)
                self.v_df.loc[r_id] = (self.v_df.loc[r_id]*(step-1) + series)/step

        else:
            if not self.sys_metrics:
                self.sys_metrics = kwargs.copy()
            else:
                for metric, value in self.sys_metrics.items():
                    self.sys_metrics[metric] = (value*(step-1) + kwargs[metric])/step

    def record_requests(self):
        return


def dict_v2type(dic):
    keys = list(dic.keys())
    types = list(map(lambda x: type(x).__name__, list(dic.values())))
    return dict(zip(keys, types))

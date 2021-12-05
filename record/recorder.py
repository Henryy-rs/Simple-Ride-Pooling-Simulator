import pandas as pd
import matplotlib.pyplot as plt
from os import path
import os
import json


class Recorder:
    def __init__(self):
        self.df = pd.DataFrame()
        self.r_df = pd.DataFrame() 
        self.v_df = pd.DataFrame()
        self.sys_metrics = {}

    def put_events(self, records, next_time, control_unit):
        if not records:
            return
        tmp_df = pd.DataFrame(columns=list(records[0].keys()))
        tmp_df = tmp_df.astype(dict_v2type(records[0]))
        tmp_requests = []       
        for record in records:
            r_state = record['r_state']
            r_id = record['r_id']
            record['time'] = next_time - record['time']
            tmp_df = tmp_df.append(record, ignore_index=True)       
            if r_state == 1:
                control_unit.manage_request(r_id)
            elif r_state == 3:
                request = control_unit.release_request(r_id)
                tmp_requests.append(request)

        tmp_df = tmp_df.set_index(['v_id', 'r_id', 'r_state'])
        self.df = pd.concat([self.df, tmp_df], axis=0)
        self.record_requests(tmp_requests)

    def put_metrics(self, step, vehicles=True, **metrics):
        if vehicles:
            if step == 1:
                tmp_df = pd.DataFrame(columns=list(metrics.keys()))
                tmp_df = tmp_df.append(metrics, ignore_index=True)
                tmp_df = tmp_df.astype(dict_v2type(metrics))
                tmp_df = tmp_df.set_index('v_id')
                self.v_df = pd.concat([self.v_df, tmp_df], axis=0)
            else:
                r_id = metrics['v_id']
                series = pd.Series(metrics)
                self.v_df.loc[r_id] = (self.v_df.loc[r_id]*(step-1) + series)/step

        else:
            if not self.sys_metrics:
                self.sys_metrics = metrics.copy()
            else:
                for metric, value in self.sys_metrics.items():
                    self.sys_metrics[metric] = (value * (step-1) + metrics[metric]) / step

    def record_requests(self, requests):
        if not requests:
            return

        tmp_df = pd.DataFrame()
        
        for request in requests:
            r_id = request.get_id()
            series = self.df.iloc[self.df.index.get_level_values('r_id') == r_id]
            match_time = series.iloc[series.index.get_level_values('r_state') == 1]['time'].to_numpy()[0]
            pick_time = series.iloc[series.index.get_level_values('r_state') == 2]['time'].to_numpy()[0]
            drop_time = series.iloc[series.index.get_level_values('r_state') == 3]['time'].to_numpy()[0]
            waiting_time = pick_time - match_time
            detour_time = drop_time - pick_time - int(request.get_best_tt())
            metrics = dict(r_id=r_id, waiting_time=waiting_time, detour_time=detour_time)
            tmp_df = tmp_df.append(metrics, ignore_index=True)
            
        tmp_df = tmp_df.astype(dict_v2type(metrics))
        tmp_df = tmp_df.set_index('r_id')
        self.r_df = pd.concat([self.r_df, tmp_df], axis=0)

    def print(self, title, save_dir):
        print("---------------------------------------------------")
        metrics = {}
        n_metrics = len(self.v_df.columns) + len(self.r_df.columns)
        fig, axes = plt.subplots(1, n_metrics, figsize=(16, 6))
        fig.suptitle(title)

        if not path.exists(save_dir):
            os.mkdir(save_dir)

        save_dir = path.join(save_dir, title)

        if not path.exists(save_dir):
            os.mkdir(save_dir)

        i = 0

        metrics['serve_time'] = self.v_df['serve_time'].mean()
        self.v_df.hist(column='serve_time', bins=60, ax=axes[i])
        axes[i].set_ylabel("n_vehicles")
        axes[i].set_xbound(0, 60)
        i += 1

        metrics['occupancy_rate'] = self.v_df['occupancy_rate'].mean()
        self.v_df.hist(column='occupancy_rate', bins=100, ax=axes[i])
        axes[i].set_ylabel('occupancy_rate')
        axes[i].set_xbound(0, 1)
        i += 1

        for col in self.r_df.columns:
            metrics[col] = self.r_df[col].mean()
            self.r_df.hist(column=col, bins=100, ax=axes[i])
            axes[i].set_ylabel("n_customers")
            i += 1

        for key, value in self.sys_metrics.items():
            metrics[key] = value

        plt.savefig(path.join(save_dir, "metrics.pdf"),  bbox_inches='tight')
        self.df.to_csv(path.join(save_dir, "logs.csv"))
        print(metrics)
        with open(path.join(save_dir, 'means.txt'), 'w') as convert_file:
            convert_file.write(json.dumps(metrics))


def dict_v2type(dic):
    keys = list(dic.keys())
    types = list(map(lambda x: type(x).__name__, list(dic.values())))
    return dict(zip(keys, types))

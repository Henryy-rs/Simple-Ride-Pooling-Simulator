import pandas as pd
import matplotlib.pyplot as plt
from os import path
import os
import json


class Recorder:
    def __init__(self, logging_mode=False):
        self.r_df = pd.DataFrame()
        self.v_df = pd.DataFrame()
        self.time_log = {}
        self.sys_metrics = {}

        self.logging_mode = logging_mode
        if self.logging_mode:
            self.log_df = pd.DataFrame()

    def put_events(self, records, next_time, control_unit):
        if not records:
            return

        tmp_requests = []

        if self.logging_mode:
            tmp_df = pd.DataFrame(columns=list(records[0].keys()))
            tmp_df = tmp_df.astype(dict_v2type(records[0]))

            for record in records:
                # event: join, pick up, drop off
                self.__memorize_event_time(record, next_time)
                r_state = record['r_state']
                r_id = record['r_id']

                tmp_df = tmp_df.append(record, ignore_index=True)

                if r_state == 1:
                    control_unit.manage_request(r_id)
                elif r_state == 3:
                    request = control_unit.release_request(r_id)
                    tmp_requests.append(request)

            tmp_df = tmp_df.set_index(['v_id', 'r_id', 'r_state'])
            self.log_df = pd.concat([self.log_df, tmp_df], axis=0)
        else:
            for record in records:
                # event: join, pick up, drop off
                self.__memorize_event_time(record, next_time)
                r_state = record['r_state']
                r_id = record['r_id']

                if r_state == 1:
                    control_unit.manage_request(r_id)
                elif r_state == 3:
                    request = control_unit.release_request(r_id)
                    tmp_requests.append(request)

        self.record_requests(tmp_requests)

    def put_metrics(self, step, vehicles=True, **metrics):
        if vehicles:
            v_id = metrics['v_id']
            if v_id in self.v_df.index:
                series = pd.Series(metrics)
                self.v_df.loc[v_id] = (self.v_df.loc[v_id]*(step-1) + series)/step
            else:
                tmp_df = pd.DataFrame(columns=list(metrics.keys()))
                tmp_df = tmp_df.append(metrics, ignore_index=True)
                tmp_df = tmp_df.astype(dict_v2type(metrics))
                tmp_df = tmp_df.set_index('v_id')
                self.v_df = pd.concat([self.v_df, tmp_df], axis=0)

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
            match_time, pick_time, drop_time = self.time_log.pop(r_id)

            assert match_time <= pick_time <= drop_time, "time_error"

            waiting_time = pick_time - match_time
            detour_time = drop_time - pick_time - int(request.get_best_tt())

            # Sometimes, detour_time can de less than zero.
            # This is because the value returned by engine.shortest_travel_time is not a global optimal solution.
            if detour_time < 0:
                detour_time = 0

            metrics = dict(r_id=r_id, waiting_time=waiting_time, detour_time=detour_time)
            tmp_df = tmp_df.append(metrics, ignore_index=True)

        tmp_df = tmp_df.astype(dict_v2type(metrics))
        tmp_df = tmp_df.set_index('r_id')
        self.r_df = pd.concat([self.r_df, tmp_df], axis=0)

    def print(self, title, save_dir):
        print("---------------------------------------------------")
        print("printing...")
        metrics = {}
        n_metrics = len(self.v_df.columns) + len(self.r_df.columns)
        fig, axes = plt.subplots(1, n_metrics, figsize=(18, 6))
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
            self.r_df.hist(column=col, bins=1000, ax=axes[i])
            axes[i].set_ybound(0, 100000)
            axes[i].set_ylabel("n_customers")
            axes[i].set_xbound(0, 1000)
            i += 1

        for key, value in self.sys_metrics.items():
            metrics[key] = value

        plt.savefig(path.join(save_dir, "metrics.pdf"),  bbox_inches='tight')

        for metric, value in metrics.items():
            value = round(value, 2)
            print("{}\t: {}".format(metric, value))
            metrics[metric] = value

        with open(path.join(save_dir, 'means.txt'), 'w') as convert_file:
            convert_file.write(title + '\n')
            convert_file.write(json.dumps(metrics))

        self.r_df.to_csv(path.join(save_dir, "request_log.csv"))
        self.v_df.to_csv(path.join(save_dir, "vehicle_log.csv"))

        if self.logging_mode:
            self.log_df.to_csv(path.join(save_dir, "log.csv"))

    def __memorize_event_time(self, record, next_time):
        r_id = record['r_id']
        record['time'] = next_time - record['time']

        if r_id not in self.time_log.keys():
            self.time_log[r_id] = []
        self.time_log[r_id].append(record['time'])

    @staticmethod
    def plot_from_csv(title, save_dir):
        r_df = pd.read_csv(path.join(save_dir, "request_log.csv"), index_col='r_id')
        v_df = pd.read_csv(path.join(save_dir, "vehicle_log.csv"), index_col='v_id')
        n_metrics = len(v_df.columns) + len(r_df.columns)
        fig, axes = plt.subplots(1, n_metrics, figsize=(18, 6))
        fig.suptitle(title)
        i = 0

        v_df.hist(column='serve_time', bins=60, ax=axes[i])
        axes[i].set_ylabel("n_vehicles")
        axes[i].set_xbound(0, 60)
        i += 1

        v_df.hist(column='occupancy_rate', bins=100, ax=axes[i])
        axes[i].set_ylabel('occupancy_rate')
        axes[i].set_xbound(0, 1)
        i += 1

        for col in r_df.columns:
            r_df.hist(column=col, bins=1000, ax=axes[i])
            axes[i].set_ybound(0, 100000)
            axes[i].set_xbound(0, 1000)
            axes[i].set_ylabel("n_customers")
            i += 1

        plt.savefig(path.join(save_dir, "metrics.pdf"),  bbox_inches='tight')


def dict_v2type(dic):
    keys = list(dic.keys())
    types = list(map(lambda x: type(x).__name__, list(dic.values())))
    return dict(zip(keys, types))

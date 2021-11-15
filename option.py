import argparse

parser = argparse.ArgumentParser(description='RPSM')
parser.add_argument('--start_time', type=int, default=1464753600 + 3600 * 5, help='start time')
parser.add_argument('--vehicles', type=int, default=10, help='number of vehicles')
parser.add_argument('--days', type=int, default=7, help='days to simulate')
parser.add_argument('--method', type=str, default='greedy', choices=['greedy', 'restricted_subgraph'], help='matching method')
parser.add_argument('--num_workers', type=int, default=0, help='number of workers')
parser.add_argument('--save_dir', type=str, default= 'results', help='directory to save results')
import argparse

parser = argparse.ArgumentParser(description='RPSM')
parser.add_argument('--start_time', type=int, default=1464753600 + 3600 * 5, help='start time')
parser.add_argument('--vehicles', type=int, default=10, help='number of vehicles')
parser.add_argument('--days', type=int, default=7, help='days to simulate')
parser.add_argument('--matching_method', type=str, default='greedy', choices=['greedy', 'angle', 'rsubgraph'], help='matching method')
parser.add_argument('--routing_method', type=str, default='greedy', choices=['greedy', 'insertion'], help='routing method')
parser.add_argument('--save_dir', type=str, default='results', help='directory to save results')
parser.add_argument('--test_mode', type=int, default=0, help='execute in test mode')
parser.add_argument('--logging_mode', type=int, default=0, help='decide whether to log')
parser.add_argument('--db_dir', type=str, default="data/db.sqlite3", help='database path')
parser.add_argument('--time_step', type=int, default=60, help='time step(sec)')
parser.add_argument('--network_path', type=str, default="data/Manhattan.graphml", help='network_path')
parser.add_argument('--paths', type=str, default="data/paths.pickle", help='paths path')
# parser.add_argument('--max_requests', type=int, default=None, help='set max requests in a step')


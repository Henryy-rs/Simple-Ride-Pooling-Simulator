import option
from common.time_utils import get_local_datetime
from control_unit import ControlUnit
import time

if __name__ == '__main__':
    args = option.parser.parse_args()

    # time settings
    test_mode = args.test_mode
    start_time = args.start_time
    current_time = start_time
    days = args.days
    time_step = args.time_step
    check_start = time.time()
    if test_mode:
        print("<TEST MODE>")
        end_time = start_time + int(60*60)
        steps = int(3600/time_step)
        days = 1
    else:
        end_time = start_time + int(60*60*24*args.days)
        steps = int((3600*24)/time_step)

    control_unit = ControlUnit(current_time=start_time, timestep=time_step, n_vehicles=args.vehicles,
                               matching_method=args.matching_method, routing_method=args.routing_method,
                               db_dir=args.db_dir, save_dir=args.save_dir, num_workers=args.num_workers,
                               test_mode=test_mode, network_path=args.network_path, paths=args.paths)

    print("Start: {}".format(get_local_datetime(start_time)))
    print("End  : {}".format(get_local_datetime(end_time)))

    for day in range(days):
        # initialize vehicles locations
        control_unit.dispatch_vehicles()
        step = 1
        for i in range(steps):
            print("---------------------------------------------------")
            print("Step: {}/{}, Datetime: {}".format(step, steps*days, get_local_datetime(current_time)))
            control_unit.step()     # TODO: logger
            step += 1
            current_time += time_step

    control_unit.print_result()
    print("run for {}s".format(int(time.time()-check_start)))



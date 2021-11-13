import option
from common.time_utils import get_local_datetime
from config.settings import TIMESTEP, db_dir
from control_unit import ControlUnit

# todo: settings.py + options.py
if __name__ == '__main__':
    args = option.parser.parse_args()

    # time settings
    start_time = args.start_time
    current_time = start_time
    end_time = end_time = start_time + int(60 * 60 * 24 * args.days)
    days = args.days
    steps = int(3600 * 24 / TIMESTEP)

    control_unit = ControlUnit(start=start_time, timestep=TIMESTEP, n_vehicles=args.vehicles,
                               matching_method=args.method, keys=args.keys, db_dir=db_dir, save_dir=args.save_dir)

    print("Start: {}".format(get_local_datetime(start_time)))
    print("End  : {}".format(get_local_datetime(end_time)))

    for day in range(days):
        # initialize vehicles locations
        control_unit.dispatch_vehicles()

        for step in range(steps):
            print("---------------------------------------------------")
            print("Step: {}/{}, Datetime: {}".format(step+1, steps*days, get_local_datetime(current_time)))
            control_unit.step(current_time)     # todo: time management module
            current_time += TIMESTEP


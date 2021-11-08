import option
from common.time_utils import get_local_datetime
from config.settings import TIMESTEP, db_dir
from request.request_loader import RequestLoader
from control_unit import ControlUnit

if __name__ == '__main__':
    # parameters
    args = option.parser.parse_args()

    # time settings
    start_time = args.start_time
    current_time = start_time
    end_time = end_time = start_time + int(60 * 60 * 24 * args.days)
    days = args.days
    steps = int(3600 * 24 / TIMESTEP)

    control_unit = ControlUnit(start=start_time, timestep=TIMESTEP, n_vehicles=args.vehicles, matching_method=args.method)
    request_loader = RequestLoader(db_dir=db_dir)

    print("Start: {}".format(get_local_datetime(start_time)))
    print("End  : {}".format(get_local_datetime(end_time)))

    for day in range(days):
        # initialize vehicles locations
        control_unit.dispatch_vehicles()
        for step in range(steps):
            # update vehicles locations
            control_unit.update_vehicles_locations()
            # load request data
            requests = request_loader.iter_request(current_time, TIMESTEP)
            # match
            #control_unit.match(requests)
            # for debugging
            control_unit.vehicles[0].print_history()

            current_time += TIMESTEP


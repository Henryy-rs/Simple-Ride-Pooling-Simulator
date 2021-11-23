def greedy_matching(requests, vehicles, timestep, engine):
    for request in requests.values():
        r_nid = request.get_origin()
        reject_time = request.get_reject_time()

        min_travel_time = reject_time
        min_v_id = -1

        for v_id, vehicle in vehicles.items():
            if vehicle.can_en_route(request):
                # location heading and time left
                v_nid, v_time_left = vehicle.get_location()
                travel_time = engine.get_shortest_travel_time(v_nid, r_nid, reject_time=reject_time) + v_time_left
                if travel_time < min_travel_time:
                    min_travel_time = travel_time
                    min_v_id = v_id

        if min_v_id != -1:
            # 추가하고 현재 위치에서 가장 가까운 목적지(아직 태우지 않은 손님 or 태운 손님 도착지)로 간다.
            vehicles[min_v_id].en_route(request, time_left=timestep)


def angle_matching(requests, vehicles, timestep, engine):
    return




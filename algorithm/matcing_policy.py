def greedy_matching(requests, vehicles, engine):
    for request in requests:
        lat, lon = request.get_origin()
        # nearest node from request (assume that pick up customer there)
        r_nid = engine.get_nearest_node(lat, lon)
        n_customers = request.get_n_customers()
        for vehicle in vehicles:
            if vehicle.can_ride(n_customers):
                # location heading and time left
                v_loc_nid, v_tl = vehicle.get_location()
                route = engine.get_shortest_route(v_loc_nid, r_nid)
                reject_time = request.get_reject_time()
                travel_time = engine.get_travel_time(route, reject_time=reject_time) + v_tl
                if travel_time >= reject_time:
                    continue
                else:
                    request.get_rid()
                    # 추가하고 현재 위치에서 가장 가까운 목적지(아직 태우지 않은 손님 or 태운 손님 도착지)로 간다.
                    vehicle.ride(request, request.get_rid(), n_customers)

    return

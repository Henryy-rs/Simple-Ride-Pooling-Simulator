from datetime import time
import common.custom_tools as ct


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

    def find_min_candidate(candidate_, v_nid_):
        r_id_, r_state_, origin_, destination_ = candidate_[0].values()
        if r_state_ == 1:
            travel_time_, route_ = engine.get_shortest_travel_time(v_nid_, origin_, return_route=True, to_list=True)
        else:
            travel_time_, route_ = engine.get_shortest_travel_time(v_nid_, destination_, return_route=True, to_list=True)
        min_tt_lst_ = travel_time_
        min_r_id_ = r_id_
        min_route_ = route_
        min_index_ = 0
        min_state_ = r_state_

        for i in range(1, len(candidate_)):
            r_id_, r_state_, origin_, destination_ = candidate_[i].values()

            if r_state_ == 1:
                travel_time_, route_ = engine.get_shortest_travel_time(v_nid_, origin_, return_route=True, to_list=True)
            else:
                travel_time_, route_ = engine.get_shortest_travel_time(v_nid_, destination_, return_route=True, to_list=True)

            if sum(travel_time_) < sum(min_tt_lst_):
                min_tt_lst_ = travel_time_
                min_r_id_ = r_id_
                min_route_ = route_
                min_index_ = i
                min_state_ = r_state_

        if min_state_ == 1:
            candidate_[min_index_]['r_state'] += 1
        else:
            candidate_.pop(min_index_)
            
        return min_r_id_, min_route_, min_tt_lst_,

    def plan_route(v_nid_, time_left_, candidate_, route_, tt_lst_, event_lst_):
        min_r_id_, min_route_, min_tt_lst_ = find_min_candidate(candidate_, v_nid_)
        route_ = ct.concate_route(route_, min_route_)
        tt_lst_ = ct.concate_tt_lst(tt_lst_, min_tt_lst_)
        event_lst_ = ct.mark_event(event_lst_, min_r_id_, len(min_route_))
        v_nid_ = route_[-1]     # next vehicle node id

        if sum(tt_lst_) + time_left_ >= timestep:
            return route_, tt_lst_, event_lst_
        else:
            if candidate_:
                return plan_route(v_nid_, time_left_, candidate_, route_, tt_lst_, event_lst_)
            else:
                return route_, tt_lst_, event_lst_

    for v_id, vehicle in vehicles.items():
        if vehicle.get_state() != 0:
            v_nid, v_time_left = vehicle.get_location()
            candidate = vehicle.get_candidests()
            # TODO: 초기화 방법 수정
            route = [0]
            tt_lst = [0]
            event_lst = [-1]
            route, tt_lst, event_lst = plan_route(v_nid, v_time_left, candidate, route, tt_lst, event_lst)
            vehicle.set_plan(route, tt_lst, event_lst)


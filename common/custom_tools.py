def concat_routes(lst1, lst2):
    lst1.pop()
    return lst1 + lst2


def concat_travel_times(tt_lst1, tt_lst2):
    tt_lst2.pop(0)
    return tt_lst1 + tt_lst2


def mark_event(event_lst, r_id, length):
    assert r_id != [], "invalid request_id"
    assert length >= 1 and type(length) == int, "invalid length"

    if length >= 2:
        for i in range(length-1):
            event_lst.append([])

    if hasattr(r_id, '__iter__'):
        for r_id_ in r_id:
            event_lst[-1].append(r_id_)
    else:
        event_lst[-1].append(r_id)

    return event_lst





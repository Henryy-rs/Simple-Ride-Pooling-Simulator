import numpy as np


def concate_route(lst1, lst2):
    lst1.pop()
    return lst1 + lst2

def concate_tt_lst(tt_lst1, tt_lst2):
    tt_lst2.pop(0)
    return tt_lst1 + tt_lst2

def mark_event(event_lst, r_id, length):
    if length == 1:
        if len(event_lst) == 1:     # 초기화 상태이면
            return [r_id]
        else:   # 경로가 있는데 그 끝에 같은 candidate 이 추가되는 경우면
            event_lst[-1] = (event_lst[-1], r_id)
            return event_lst    # 리턴 안해줘도 event list 가 바뀌긴 함
    else:
        return event_lst + [-1] * (length - 2) + [r_id]




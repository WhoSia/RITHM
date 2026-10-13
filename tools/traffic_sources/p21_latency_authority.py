"""No observed provider publication or certified delay -> no live deployability."""
from datetime import datetime, timedelta

def lag_from_certified_bound(upper_minutes,*,verified=False):
    if verified is not True:raise ValueError("Certified provider upper delay needed")
    if isinstance(upper_minutes,bool) or not isinstance(upper_minutes,int):
        raise TypeError("Integer minute source age required")
    if upper_minutes<0:raise ValueError("Negative source delay")
    return 1+(upper_minutes+9)//10

def pair_available_by(decision_time,first_end,first_public,second_end,second_public):
    for x in (decision_time,first_end,first_public,second_end,second_public):
        if not isinstance(x,datetime) or x.tzinfo is None or x.utcoffset() is None:
            raise TypeError("Timezone-aware source clock needed")
    if second_end-first_end!=timedelta(minutes=5):
        raise ValueError("Noncontiguous source halves cannot form exact ten-minute total")
    if first_public<first_end or second_public<second_end:
        raise ValueError("Publication before recorded observation interval end")
    return second_end<=decision_time and first_public<=decision_time and second_public<=decision_time

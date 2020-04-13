import datetime as dt
from datetime import datetime


class JourneyRequest:
    def __init__(
        self,
        origin_id: str,
        dest_id: str,
        arr_dep: str,
        time: datetime = datetime.now(),
    ):
        self.origin_id = origin_id
        self.dest_id = dest_id
        self.arr_dep = arr_dep
        self.time = time

    def to_efa_params(self):
        def format_daytime(time: datetime):
            return time.strftime("%H%M")

        return {
            "routeType": "leasttime",
            "type_destination": "any",
            "type_origin": "any",
            "itdDate": self.time.strftime("%Y%m%d"),
            "itdDateTimeDepArr": self.arr_dep,
            "itdTime": format_daytime(self.time),
            "itdTripDateTimeDepArr": self.arr_dep,
            "name_destination": self.dest_id,
            "name_origin": self.origin_id,
        }

    # TODO
    # def to_cal_event(self,

from datetime import datetime, timezone
from copy import copy

class Journey:

    origin = None
    dest = None
    dep_time = None
    arr_time = None
    duration = None
    transportation = None
    legs = [] # array of JourneyInfo

    def __init__(self, origin=None, dest=None,
        dep_time:datetime=None, arr_time:datetime=None):
        self.origin = origin
        self.dest = dest
        self.dep_time = dep_time
        self.arr_time = arr_time
        if arr_time is not None and dep_time is not None:
            self.duration = divmod((arr_time - dep_time).total_seconds(), 60)[0]

        self.legs = []
        self.transportation = None

    def set_transportation(self, transportation):
        self.transportation = transportation

    def set_legs(self, legs):
        self.legs = legs

    def add_leg(self, leg):
        self.legs.append(leg)

    def get_duration(self):
        if self.duration:
            return self.duration
        if self.arr_time and self.dep_time:
            self.duration = divmod((self.arr_time - self.dep_time).total_seconds(), 60)[0]
            return self.duration

        raise Error("duration can not be calculated")

    def get_arr_time(self):
        return self.arr_time

    def __str__(self):
        description = str(self.origin
                + ' at '    + str(self.dep_time.strftime("%H:%M"))
                + ' to '    + self.dest
                + ' by '    + str(self.transportation)
                + ' until ' + str(self.arr_time.strftime("%H:%M"))
                + ' takes ' + str(self.get_duration()))

        for leg in self.legs:
            description += "\n" + str(leg)

        return description

    def to_link(self):
        link = ''.join("""https://www3.vvs.de/mng/#!/XSLT_TRIP_REQUEST2@details?
            deeplink={
                **dateTime**:{
                    **date**:**DATE**,
                    **dateFormat**:****,
                    **time**:**TIME**,
                    **timeFormat**:****,
                    **useRealTime**:true,
                    **isDeparture**:true
                },
                **odvs**:{
                    **orig**:**ORIGIN**,
                    **dest**:**DEST**
                }
            }""".split())
        link = link.replace("DATE", self.dep_time.strftime("%d.%m.%Y"))
        link = link.replace("TIME", self.dep_time.strftime("%H:%M"))
        link = link.replace("ORIGIN", self.origin)
        link = link.replace("DEST", self.dest)
        return link

    def from_vvs(self, vvs_journey:dict):
        def from_utc_to_local(utc_dt):
            return utc_dt.replace(tzinfo=timezone.utc).astimezone()

        def parse_vvs_time(datestr:str):
            datestr = datestr.replace("Z", "+00:00")
            vvs_time = datetime.fromisoformat(datestr)
            #vvs_time = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
            return from_utc_to_local(vvs_time)

        legs = vvs_journey.get('legs', [])
        origin = legs[0].get('origin')
        dest = legs[-1].get('destination')
        self.origin = origin.get('name')
        self.dest = dest.get('name')
        self.transportation = list(map(lambda l:
            l.get('transportation').get('name', 'foot'), legs))
        self.dep_time = parse_vvs_time(origin.get('departureTimePlanned'))
        self.arr_time = parse_vvs_time(dest.get('arrivalTimePlanned'))

        for leg in vvs_journey.get('legs'):
            origin = copy(leg.get('origin').get('name'))
            dest = copy(leg.get('destination').get('name'))
            dep_time = parse_vvs_time(leg.get('origin').get('departureTimePlanned'))
            arr_time = parse_vvs_time(leg.get('destination').get('arrivalTimePlanned'))

            leg_journey = Journey(origin, dest, dep_time, arr_time)
            leg_journey.set_transportation(leg.get('transportation')
                .get('name', 'foot'))
            self.legs.append(leg_journey)

        return self


from datetime import datetime, timezone
import copy
import pytz

from services.cal import Event

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
            self.duration = arr_time - dep_time

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
            self.duration = self.arr_time - self.dep_time
            return self.duration

        raise Error("duration can not be calculated")

    def get_arr_time(self):
        return self.arr_time

    def __str__(self):
        journey = self.localize()

        description = (f'{journey.origin}'
                f' at {journey.dep_time.strftime("%H:%M")}'
                f' to {journey.dest}'
                f' by {journey.transportation}'
                f' until {journey.arr_time.strftime("%H:%M")}'
                f' takes {journey.get_duration()}')

        for leg in journey.legs:
            description += "\n" + str(leg)

        return description

    def get_user_tz(self):
        return pytz.timezone("Europe/Berlin")

    def localize(self):
        new = copy.deepcopy(self)

        new.dep_time = self.dep_time.astimezone(self.get_user_tz())
        new.arr_time = self.arr_time.astimezone(self.get_user_tz())

        for leg in new.legs:
            leg = leg.localize()

        return new

    def to_table(self):
        journey = self.localize()

        dep_time = journey.dep_time.strftime("%H:%M")
        arr_time = journey.dep_time.strftime("%H:%M")

        table = {
            'Origin': [self.origin],
            'Destination': [self.dest],
            'Departure': [dep_time],
            'Arrival': [arr_time],
            'Means': [self.transportation],
            'Duration': [str(self.get_duration())]
        }

        for leg in self.legs:
            leg_table = leg.to_table()
            for k, l in leg_table.items():
                table[k] += l

        return table

    def to_event(self):
        event = Event()
        event.set_title('From ' + self.origin + ' to ' + self.dest)
        event.set_start(self.dep_time)
        event.set_end(self.arr_time)
        event.set_description(str(self))
        return event

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
        link = link.replace("ORIGIN", self.origin_id)
        link = link.replace("DEST", self.dest_id)
        return link

    def from_vvs(self, vvs_journey:dict):

        def parse_vvs_time(datestr:str):
            datestr = datestr.replace("Z", "+00:00")
            vvs_time = datetime.fromisoformat(datestr)
            #vvs_time = datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%SZ")
            return vvs_time.astimezone(pytz.utc)

        legs = vvs_journey.get('legs', [])
        origin = legs[0].get('origin')
        dest = legs[-1].get('destination')

        self.origin = origin.get('name')
        self.dest = dest.get('name')
        self.origin_id = origin.get('id')
        self.dest_id = dest.get('id')

        self.transportation = list(map(lambda l:
            l.get('transportation').get('name', 'foot'), legs))
        self.dep_time = parse_vvs_time(origin.get('departureTimePlanned'))
        self.arr_time = parse_vvs_time(dest.get('arrivalTimePlanned'))

        for leg in vvs_journey.get('legs'):
            origin = copy.copy(leg.get('origin').get('name'))
            dest = copy.copy(leg.get('destination').get('name'))
            dep_time = parse_vvs_time(leg.get('origin').get('departureTimePlanned'))
            arr_time = parse_vvs_time(leg.get('destination').get('arrivalTimePlanned'))

            leg_journey = Journey(origin, dest, dep_time, arr_time)
            leg_journey.set_transportation(leg.get('transportation')
                .get('name', 'foot'))
            self.legs.append(leg_journey)

        return self


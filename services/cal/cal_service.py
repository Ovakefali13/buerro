from datetime import datetime as dt, timedelta
import pytz
import caldav
from caldav.elements import dav, cdav
from dotenv import load_dotenv
from os import environ
from abc import ABC, abstractmethod

from . import Event

class CaldavRemote(ABC):

    @abstractmethod
    def add_event(self, event:Event):
        pass

    @abstractmethod
    def events(self):
        pass

    @abstractmethod
    def date_search(self, start:dt, end:dt=None):
        pass

class iCloudCaldavRemote(CaldavRemote):
    def __init__(self):
        def _get_named_calendar(calendars, name):
            calendars = principal.calendars()
            for cal in calendars:
                properties = cal.get_properties([dav.DisplayName(), ])
                display_name = properties['{DAV:}displayname']
                if(display_name == name):
                    return cal

        load_dotenv()

        required_env = (
                'CALDAV_URL',
                'USERNAME',
                'PASSWORD',
                'CALENDAR'
        )

        if not all([var in environ for var in required_env]):
            raise EnvironmentError("Did not set all of these environment variables: ", required_env)

        client = caldav.DAVClient(
            environ['CALDAV_URL'],
            username=environ['USERNAME'],
            password=environ['PASSWORD'])

        principal = client.principal()
        self.calendar = _get_named_calendar(principal.calendars(), environ['CALENDAR'])
        if self.calendar is None:
            raise EnvironmentError('Provided CALENDAR could not be found')

    def add_event(self, event:Event):
        ical = "BEGIN:VCALENDAR\n"+event.to_ical()+"\nEND:VCALENDAR"
        self.calendar.add_event(ical)

    def from_caldav(self, caldav_events):
        def _ev_from_caldav(icloud_ev):
            if icloud_ev.vobject_instance:
                obj = icloud_ev.vobject_instance
                if obj.name.lower() == 'vcalendar':
                    vevents = list(filter(lambda child: child.name.lower() == 'vevent',
                        obj.getChildren()))
                    if len(vevents) == 0:
                        raise Exception("Found no VEVENT")
                    if len(vevents) > 1:
                        raise Exception("Unexpectedly found two VEVENT in a "
                            +"VCALENDER")
                    vevent = vevents[0]
                    ev = Event().from_ical(vevent.serialize())
                    return ev
            return None

        return list(filter(lambda e : e is not None,
            map(_ev_from_caldav, caldav_events)))

    def events(self):
        return self.from_caldav(self.calendar.events())

    def date_search(self, start:dt, end:dt=None):
        return self.from_caldav(self.calendar.date_search(start, end))

    def purge(self):
        for event in self.calendar.events():
            if event.vobject_instance: # don't delete the calendar object
                event.delete()

class CalService:

    def __init__(self, remote:CaldavRemote):
        self.remote = remote

    def get_next_events(self):
        return self.get_events_between(dt.now(pytz.utc))

    def get_events_between(self, start:dt, end:dt=None):
        events = self.remote.date_search(start, end)
        return sorted(events, key=lambda e: e['dtstart'].dt)

    def get_all_events(self):
        return self.remote.events()

    def add_event(self, event:Event):
        event.check_parameters_and_raise()
        self.remote.add_event(event)

    def get_max_available_time_between(self, start:dt, end:dt):
        events = self.get_events_between(start, end)

        if not events:
            return end - start, None, None

        max_delta = events[0].get_start() - start
        event_before = None
        event_after = events[0]

        time_until_end = end - events[-1].get_end()
        if time_until_end > max_delta:
            max_delta = time_until_end
            event_before = events[-1]
            event_after = None

        for previous, current in zip(events, events[1:]):
            delta = current.get_start() - previous.get_end()
            if delta > max_delta:
                max_delta = delta
                event_before = previous
                event_after = current

        return max_delta, event_before, event_after

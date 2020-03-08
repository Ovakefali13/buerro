from datetime import datetime as dt, timedelta
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
        return list(filter(lambda e : e is not None,
            map(Event.from_caldav, caldav_events)))

    def events(self):
        return self.from_caldav(self.calendar.events())

    def date_search(self, start:dt, end:dt):
        return self.from_caldav(self.calendar.date_search(start, end))

class CalService:

    def __init__(self, remote:CaldavRemote):
        self.remote = remote

    def get_next_event(self):
        #TODO
        pass

    def get_events_between(self, start:dt, end:dt):
        return self.remote.date_search(start, end)

    def get_all_events(self):
        return self.remote.events()

    def add_event(self, event:Event):
        self.remote.add_event(event)



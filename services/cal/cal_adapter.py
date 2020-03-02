from datetime import datetime
import caldav
from caldav.elements import dav, cdav
from dotenv import load_dotenv
from os import environ

from .event import Event

class CalAdapter:
    client = None
    calendar = None

    def __init__(self):
        load_dotenv()

        required_env = (
                'CALDAV_URL',
                'USERNAME',
                'PASSWORD',
                'CALENDAR'
        )

        if not all([var in environ for var in required_env]):
            raise EnvironmentError("Did not set all of these environmet variables: ", required_env)

        client = caldav.DAVClient(environ['CALDAV_URL'], username=environ['USERNAME'], password=environ['PASSWORD'])
        principal = client.principal()
        calendars = principal.calendars()

        for cal in calendars:
            properties = cal.get_properties([dav.DisplayName(), ])
            display_name = properties['{DAV:}displayname']
            if(display_name == environ['CALENDAR']):
                self.calendar = cal
                break

        if self.calendar is None:
            raise EnvironmentError('Provided CALENDAR could not be found')

    def get_next_event(self):
        #TODO
        pass

    def get_events_in_next_minutes(self, minutes:int):
        now = datetime.now()
        in_min = now + timedelta(minutes=minutes)
        return self.calendar.date_search(now, in_min)

    def get_events_in_next_hours(self, hours:int):
        now = datetime.now()
        in_h = now + timedelta(hours=hours)
        return self.calendar.date_search(now, in_h)

    def get_all_events(self):
        return self.calendar.events()


    def add_event(self, Event):
        self.calendar.add_event(event.to_ical())


if __name__ == "__main__":
    adapter = CaldavAdapter()
    print(adapter.get_all_events())
    adapter.add_event(Event("Main Event", 
            start=datetime(2020, 2, 26, 18, 00), 
            end=datetime(2020, 2, 26, 19, 00),
            location="My Hood", reminder_min=10))



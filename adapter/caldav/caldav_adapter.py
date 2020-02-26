from datetime import datetime
import caldav
from caldav.elements import dav, cdav
from dotenv import load_dotenv
from os import environ

class CaldavAdapter:
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

    def format_date(self, dt):
        return dt.strftime("%Y%m%dT%H%M%SZ")

    def add_event(self, title:str, start:datetime, end:datetime, location:str="",
            reminder_min:int=None):

        event = {
            'summary':  title, 
            'dtstart':  self.format_date(start),
            'dtend':    self.format_date(end), 
            'dtstamp':  self.format_date(datetime.now()),
            'uid':      self.format_date(datetime.now())+"@buerro",
            'location': location,
            'reminder_min': reminder_min
        }

        ical_ev = """BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:{summary}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
LOCATION:{location}
UID:{uid}
BEGIN:VALARM
TRIGGER:-PT{reminder_min}M
ACTION:AUDIO
END:VALARM
END:VEVENT
END:VCALENDAR"""
        ical_ev = ical_ev.format(**event)
        
        print(ical_ev)

        self.calendar.add_event(ical_ev)


if __name__ == "__main__":
    adapter = CaldavAdapter()
    print(adapter.get_all_events())
    adapter.add_event("Main Event", 
            start=datetime(2020, 2, 26, 18, 00), 
            end=datetime(2020, 2, 26, 19, 00),
            location="My Hood", reminder_min=10)



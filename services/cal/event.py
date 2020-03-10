import datetime
from datetime import timedelta, datetime as dt
from icalendar import Event as iCalEvent
from icalendar import Alarm, vDatetime
import pytz
import random
import string

class Event(iCalEvent):
    def __init__(self, ical_ev:iCalEvent=None):
        if ical_ev:
            # TODO losing some information here
            super().__init__()
            for key in ical_ev:
                self.add(key, ical_ev[key])
        else:
            super().__init__()
            now = dt.now().astimezone()
            self.add('dtstamp', now)
            random_id = ''.join(random.choices(string.ascii_uppercase + string.digits,k=12))
            self.add('uid', vDatetime(now).to_ical().decode('utf-8')+random_id+'@buerro.com')
            #self.add('uid', '00008')

    def to_ical(self):
        ical = super().to_ical()
        ical = ical.replace(b'\r\n',b'\n').strip()
        ical = ical.decode('utf-8')
        return ical

    def set_reminder(self, reminder:timedelta):
        # all types: https://github.com/collective/icalendar/blob/2aa726714ff4a17e47b256da529640b201ebf66b/src/icalendar/prop.py 
        alarm = Alarm()
        alarm.add('trigger', -reminder)
        alarm.add('action', 'AUDIO')
        #TODO alarm.add('repeat', 2)
        self.add_component(alarm)

    @classmethod
    def from_ical(self, st):
        return self(super().from_ical(st))

    def check_parameters_and_raise(self):
        min_params = ('summary', 'dtstart', 'dtend')
        has_min = all(key in self for key in min_params)
        if not has_min:
            raise Exception("Event does not have minimal parameters "
                    +min_params)

    def summarize(self):
        self.check_parameters_and_raise()
        start = self['dtstart'].dt.strftime("%H:%M")
        end = self['dtend'].dt.strftime("%H:%M")
        if 'location' in self:
            location = ' at '+self['location']
        else:
            location = ''
        return "{summary} from {start} until {end}{location}".format(
            summary=self['summary'],
            start=start, end=end,
            location=location)



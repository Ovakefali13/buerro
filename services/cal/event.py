import datetime
from datetime import timedelta, datetime as dt
from icalendar import Event as iCalEvent
from icalendar import Alarm, vDatetime

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
            self.add('uid', vDatetime(now).to_ical().decode('utf-8')+'@buerro.com')
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

    @classmethod
    def from_caldav(self, icloud_ev):
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
                ev = self().from_ical(vevent.serialize())
                return ev
        return None

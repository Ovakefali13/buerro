import datetime

class Event:

    def __init__(self, title:str, start:datetime, end:datetime, location:str=""):
        self.title = title
        self.start = start
        self.end = end
        self.location = location
        self.reminder = None
        self.stamp = datetime.datetime.now()
    
    def format_date(self, dt):
        #2020-02-26T18:00:00Z
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_ical(self):
        event = {
            'summary':  self.title, 
            'dtstart':  self.format_date(self.start),
            'dtend':    self.format_date(self.end), 
            'dtstamp':  self.format_date(self.stamp),
            'uid':      self.format_date(self.stamp)+"@buerro",
            'location': self.location,
            'alarm_ical': self.get_alarm_ical()
        }
        
        ical_ev = """BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:{summary}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
LOCATION:{location}
UID:{uid}
{alarm_ical}
END:VEVENT
END:VCALENDAR"""
        return ical_ev.format(**event)

    # reminder should be a datetime.timedelta
    def set_reminder(self, reminder:datetime.timedelta):
        self.reminder = reminder

    def get_alarm_ical(self):
        if not self.reminder:
            return ""

        reminder_min = int(self.reminder.total_seconds() / 60)
        alarm_ical = """BEGIN:VALARM
TRIGGER:-PT{reminder_min}M
ACTION:AUDIO
END:VALARM"""
        return alarm_ical.format(reminder_min=reminder_min)

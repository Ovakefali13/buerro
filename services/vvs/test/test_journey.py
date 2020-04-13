import unittest
import json
import os
from datetime import datetime as dt, timedelta
import pytz

from .. import Journey
from services.cal import Event

class TestJourney(unittest.TestCase):
    dirname = os.path.dirname(__file__)
    with open(os.path.join(dirname, 'mock_journeys.json'), 'r') as mock_journeys_f:
        mock_journeys = json.load(mock_journeys_f).get('journeys')

    def test_from_vvs(self):
        journeys = []
        for mock_json in self.mock_journeys:
           journeys.append(Journey().from_vvs(mock_json))
        self.assertTrue(len(journeys) == 3)

        for journey in journeys:
            self.assertIsNotNone(journey)
            self.assertIsInstance(journey, Journey)

        journey = journeys[0]
        self.assertEqual(journey.origin, 'Stadtmitte')
        self.assertEqual(journey.dest, 'Stuttgart Hauptbahnhof (tief)')
        self.assertEqual(len(journey.legs), 1)

    def test_to_str_to_event_and_to_table(self):
        start = dt(2020, 2, 1, 8, 0, tzinfo=pytz.utc)

        journey = Journey('A', 'B', start, start+timedelta(minutes=15))
        journey.set_transportation("['U1', 'U2']")
        leg1  = Journey('A', 'C', start, start+timedelta(minutes=5))
        leg1.set_transportation('U1')
        leg2  = Journey('C', 'B', start+timedelta(minutes=5),
            start+timedelta(minutes=15))
        leg2.set_transportation('U2')
        journey.set_legs([leg1, leg2])

        time = "[0-9]{1,2}:[0-9]{1,2}"
        duration = "[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}"
        expected = str(
            f"A at {time} to B by \['U1', 'U2'\] until {time} takes {duration}\\n"
        +   f"A at {time} to C by U1 until {time} takes {duration}\\n"
        +   f"C at {time} to B by U2 until {time} takes {duration}"
        )

        self.assertRegex(str(journey), expected)

        def filter_ical(ical):
            rest = []
            for line in ical.splitlines():
                non_indicative_ical_fields = ['UID', 'DTSTAMP', 'DESCRIPTION']
                if all([(ignore_field not in line) for ignore_field in non_indicative_ical_fields]):
                    if len(line) > 0:
                        rest.append(line)
            return rest

        with self.subTest("can transform into cal event"):
            exp_ev = Event()
            exp_ev.set_title('From A to B')
            #exp_ev.set_description(expected)
            exp_ev.set_start(start)
            exp_ev.set_end(start + timedelta(minutes=15))

            exp_ev = exp_ev.to_ical()
            actual_ev = journey.to_event()
            del actual_ev['description']
            actual_ev = actual_ev.to_ical()

            for l_exp, l_act in zip(filter_ical(exp_ev),
                                    filter_ical(actual_ev)):
                self.assertEqual(l_exp, l_act)

        with self.subTest("can transform into a table"):
            expected = {
                'Origin': ['A', 'A', 'C'],
                'Destination': ['B','C', 'B'],
                'Departure': [time, time, time],
                'Arrival': [time, time, time],
                'Means': ["['U1', 'U2']", 'U1', 'U2'],
                'Duration': [duration, duration, duration]
            }

            actual = journey.to_table()
            for (k1, l_exp), (k2, l_act) in zip(expected.items(), actual.items()):
                self.assertEqual(len(l_exp), len(l_act))
                for v_exp, v_act in zip(l_exp, l_act):
                    self.assertRegex(v_act, v_exp)

    def test_to_link(self):
        dep_time = dt(2020, 3, 16, 7, 7)
        journey = Journey("Stadmitte","Hauptbahnhof", dep_time, None)

        journey.origin_id = "de:08111:6056"
        journey.dest_id = "de:08111:13"

        self.maxDiff = None
        expected = """https://www3.vvs.de/mng/#!/XSLT_TRIP_REQUEST2@details?
                        deeplink={
                            **dateTime**:{
                                **date**:**16.03.2020**,
                                **dateFormat**:****,
                                **time**:**07:07**,
                                **timeFormat**:****,
                                **useRealTime**:true,
                                **isDeparture**:true
                            },
                            **odvs**:{
                                **orig**:**de:08111:6056**,
                                **dest**:**de:08111:13**
                            }
                        }"""

        expected = ''.join(expected.split())
        self.assertEqual(journey.to_link(), expected)

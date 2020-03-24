import unittest
from urllib.parse import urlparse
from datetime import datetime as dt, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import os
import queue

from .. import WorkSession
from usecase import Usecase, Reply, FinishedException
from handler import BaseNotificationHandler, Notification
from util import Singleton
from services.todoAPI import TodoistService, TodoistJSONRemote
from services.todoAPI.test import TodoistMockRemote
from services.music import MusicService, SpotifyRemote
from services.music.test import MusicMockRemote
from services.cal import CalService, Event, iCloudCaldavRemote
from services.cal.test import CalMockRemote
from services.vvs import VVSService, VVSEfaJSONRemote, Journey
from services.vvs.test import VVSMockRemote
from services.preferences import PrefService, PrefRemote

class MockPrefRemote(PrefRemote):
    def load_file(self):
        return {
            "general": {},
            "work_session": {
                "min_work_period_minutes": 30,
                "be_minutes_early": 10,
                "remind_min_before_leaving": 15,
                "pomodoro_minutes": 0.1 / 60,
                "break_minutes": 0.1 / 60
            }
        }
    def merge_json_files(self, dict1, dict2):
        return {**dict1, **dict2}

@Singleton
class MockVVSService:
    def get_location_id(self, location):
        if location == "Stuttgart Hauptbahnhof":
            return 'de:08111:6118'
        elif location == "Rotebühlplatz":
            return 'de:08111:6056'

    def get_journeys_for_id(self, origin_id, dest_id, arr_dep:str, by:dt):
        return [
            Journey(origin_id, dest_id,
                dep_time=by - timedelta(minutes=30),
                arr_time=by - timedelta(minutes=15)
            ),
            Journey(origin_id, dest_id,
                dep_time=by - timedelta(minutes=25),
                arr_time=by - timedelta(minutes=10)
            )
        ]

    def recommend_journey_to_arrive_by(self, journeys, by:dt):
        return journeys[-1]

@Singleton
class MockNotificationHandler(BaseNotificationHandler):
    def set_queue(self, notification_queue:queue.Queue):
        self.notification_queue = notification_queue
    def push(self, notification:Notification):
        if not self.notification_queue:
            raise Exception("no notification queue set")
        self.notification_queue.put(notification)


class TestWorkSession(unittest.TestCase):
    """This use case should best be understood with a flow chart:
    https://preview.tinyurl.com/uvsyfyk
    """

    @classmethod
    def setUpClass(self):
        def setup_scheduler():
            scheduler = BackgroundScheduler()
            scheduler.start()
            return scheduler

        def setup_notification_handler():
            notification_host = "localhost"
            notification_port = 8745
            self.server_url = "http://" + notification_host + ":" + str(notification_port)

            self.notification_queue = queue.Queue()

            notification_handler = MockNotificationHandler.instance()
            notification_handler.set_queue(self.notification_queue)
            return notification_handler

        self.notification_handler = setup_notification_handler()
        self.scheduler = setup_scheduler()

        if 'DONOTMOCK' in os.environ:
            self.cal_service = CalService.instance(
                iCloudCaldavRemote.instance())
            vvs_service = VVSService.instance(
                VVSEfaJSONRemote.instance())
            todo_service = TodoistService.instance(
                TodoistJSONRemote.instance())
            music_service = MusicService.instance(
                SpotifyRemote.instance())
        else:
            self.cal_service = CalService.instance(
                CalMockRemote.instance())
            vvs_service = MockVVSService.instance()
            #vvs_service = VVSService.instance(
            #    VVSMockRemote.instance())
            todo_service = TodoistService.instance(
                TodoistMockRemote.instance())
            music_service = MusicService.instance(
                MusicMockRemote.instance())

        pref_service = PrefService(MockPrefRemote())

        usecase = WorkSession()
        usecase.set_services(
            pref_service=pref_service,
            cal_service=self.cal_service,
            vvs_service=vvs_service,
            todo_service=todo_service,
            music_service=music_service
        )

        usecase.set_scheduler(self.scheduler)
        usecase.set_notification_handler(self.notification_handler)

        self.usecase = usecase

    @classmethod
    def setUp(self):
        self.cal_service.purge()
        self.usecase.reset()

    def uri_valid(self, x):
        try:
            result = urlparse(x)
            return all([result.scheme, result.netloc, result.path])
        except:
            return False

    def test_starting_not_worth_it(self):
        event_in_mins = 30
        self.usecase.pref['min_work_period_minutes'] = event_in_mins

        event = Event()
        event.set_start(pytz.utc.localize(dt.now()) +
            timedelta(minutes=event_in_mins-1))
        event.set_end(event.get_start() + timedelta(minutes=30))
        event.set_title('too soon event')
        self.cal_service.add_event(event)

        reply = self.usecase.advance(None)
        expected = "Your next appointment is too close to start working:"
        self.assertIn(expected, reply.message)
        self.assertIn('too soon event', reply.message) # also displays event
        self.assertTrue(self.usecase.is_finished())

    def test_ask_wether_we_can_make_it_there(self):
        event_in_mins = 30
        self.usecase.pref['min_work_period_minutes'] = event_in_mins

        event = Event()
        event.set_start(pytz.utc.localize(dt.now()) +
            timedelta(minutes=event_in_mins+30))
        event.set_end(event.get_start() + timedelta(minutes=30))
        event.set_title('possibly too soon event')
        self.cal_service.add_event(event)

        reply = self.usecase.advance(None)
        expected = "Your next appointment might be too close to start working:"
        self.assertIn(expected, reply.message)
        self.assertIn('possibly too soon event', reply.message) # also displays event
        self.assertIn('Do you still want to start working?', reply.message)

    def test_no_upcoming_events(self):
        reply = self.usecase.advance(None)
        expected = "You have no upcoming events."
        self.assertIn(expected, reply.message)

    @unittest.skipIf('TRAVIS' in os.environ and 'DONOTMOCK' in os.environ,
                    "travis IP might be blocked on iCloud")
    def test_creates_reminder_for_upcoming(self):
        event = Event()
        event.set_start(dt.now(pytz.utc) + timedelta(minutes=270))
        event.set_end(event.get_start() + timedelta(minutes=30))
        event.set_title('upcoming event')
        event.set_location('Stuttgart Hauptbahnhof')
        self.cal_service.add_event(event)

        reply = self.usecase.advance(None)
        expected = "I created a reminder for when you have to get going to reach:"
        self.assertIn(expected, reply.message)
        self.assertIn('upcoming event', reply.message)
        self.assertIn('until', reply.message)
        self.assertIn('takes', reply.message)

        events = self.cal_service.get_all_events()
        events = list(filter(lambda e: 'Hauptbahnhof' in e.get_title(), events))
        self.assertIsNotNone(events)

        # TODO assert reminder is set
        # self.notificationHandler.get_notifications().contains()

    def test_advances_correctly(self):
        states = {
            'music': "Would you like to listen to music?",
            'music_rec': "How about this Spotify playlist?",

            'project': "Which project do you want to work on?",
            'todos': "Here are your Todo's",

            'pomodoro': "Do you want to start a pomodoro session?",
            'fin_no_pom': "I hope you'll have a productive session!",

            'pom_start': "I will notify you in",
            'pom_block': "I will notify you in",
            'pom_fin': ("Good Work! You finished your session."
                        "\nDo you want to take a break, skip it or finish?"),

            'break_start': "I will notify you in",
            'break_block': "I will notify you in",
            'break_fin': "Your break is over. Do you want to get back to work?"
        }

        uc = self.usecase

        reply = uc.advance(None)
        self.assertIn(states['music'], reply.message)

        reply = uc.advance('yes')
        self.assertIn(states['music_rec'], reply.message)
        self.assertIsNotNone(reply.link)
        self.assertTrue(self.uri_valid(reply.link))
        self.assertIn(states['project'], reply.message)

        reply = uc.advance('Software Engineering')
        self.assertIn(states['todos'], reply.message)
        self.assertIn(states['pomodoro'], reply.message)

        for pomodoro in (False, True):
            with self.subTest('Pomodoro? '+str(pomodoro)):
                if not pomodoro:
                    reply = uc.advance('no')
                    self.assertIn(states['fin_no_pom'], reply.message)
                    self.assertTrue(uc.is_finished())

                else:
                    uc._set_state('pomodoro')
                    for pomodoro_i in range(5):
                        reply = uc.advance('yes')
                        self.assertIn(states['pom_start'], reply.message)

                        self.assertTrue(self.notification_queue.empty())
                        for i in range(10):
                            if not self.notification_queue.empty():
                                break
                            reply = uc.advance('asdfpoijw')
                            self.assertIn(states['pom_block'], reply.message)

                        # assert notification reached Notification Handler
                        notification = self.notification_queue.get(
                                            block=True, timeout=0.2)
                        self.assertTrue(self.notification_queue.empty())
                        self.assertIn(states['pom_fin'], notification['title'])
                        self.assertIn(states['pom_fin'],
                                        notification['options']['data']['message'])

                        self.assertEqual(uc.get_state().lower(), "break")

                        for take_break in (True, False):
                            with self.subTest(str(pomodoro_i)+' Break? '+str(take_break)):
                                if take_break:
                                    reply = uc.advance('I want to take a break')
                                    self.assertIn(states['break_start'], reply.message)

                                    self.assertTrue(self.notification_queue.empty())
                                    for i in range(10):
                                        if not self.notification_queue.empty():
                                            break
                                        reply = uc.advance('asdfpoijw')
                                        self.assertIn(states['break_block'], reply.message)

                                    # assert notification reached Notification Handler
                                    notification = self.notification_queue.get(
                                                        block=True, timeout=0.2)
                                    self.assertTrue(self.notification_queue.empty())
                                    self.assertIn(states['break_fin'], notification['title'])
                                    self.assertIn(states['break_fin'],
                                                    notification['options']['data']['message'])
                                else:
                                    uc._set_state('break')
                                    reply = uc.advance('skip')

                        self.assertEqual(uc.get_state().lower(), "pomodoro")

                        """
                        #TODO should also ask for which project to work on
                        #reply = reply || notification
                        #self.assertIn(states['which_project'], notification.message)
                        self.assertIn(states['project'], reply.message)
                        self.assertIsNotNone(reply.list) # list of projects

                        reply = uc.advance('Software Engineering')
                        self.assertIn(states['pomodoro'], reply.message)
                        """

                    # finally no more pomodoros...
                    reply = uc.advance('no')
                    self.assertIn(states['fin_no_pom'], reply.message)
                    self.assertTrue(uc.is_finished())

                # starts over...
                self.assertRaises(FinishedException, uc.advance, None)
                uc.reset()
                reply = uc.advance(None)
                self.assertIn(states['music'], reply.message)


import unittest
from unittest.mock import patch
from urllib.parse import urlparse
from datetime import datetime as dt, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
import os
import queue
from freezegun import freeze_time

from .. import WorkSession
from usecase import Usecase, Reply, FinishedException
from handler import BaseNotificationHandler, Notification, LocationHandler
from util import Singleton
from services.todoAPI import TodoistService, TodoistJSONRemote
from services.todoAPI.test import TodoistMockRemote
from services.music import MusicService, SpotifyRemote
from services.music.test import MusicMockRemote
from services.cal import CalService, Event, iCloudCaldavRemote
from services.cal.test import CalMockRemote
from services.vvs import VVSService, VVSEfaJSONRemote, Journey
from services.vvs.test import VVSMockRemote
from services.maps import GeocodingService, GeocodingJSONRemote
from services.preferences import PrefService, PrefRemote


class MockPrefRemote(PrefRemote):
    def load_file(self):
        return {
            "general": {},
            "work_session": {
                "min_work_period_minutes": 30,
                "be_minutes_early": 10,
                "remind_min_before_leaving": 15,
                "pomodoro_minutes": 25,
                "break_minutes": 5,
            },
        }

    def merge_json_files(self, dict1, dict2):
        return {**dict1, **dict2}


@Singleton
class MockGeocodingService:
    def get_address_from_coords(self, coords: tuple):
        return "Rotebühlplatz 41, 70178 Stuttgart"


@Singleton
class MockVVSService:
    def get_location_id(self, location):
        if location == "Stuttgart Hauptbahnhof":
            return "de:08111:6118"
        elif location == "Rotebühlplatz":
            return "de:08111:6056"

    def get_journeys_for_id(self, origin_id, dest_id, arr_dep: str, by: dt):
        origin = "Stuttgart Hauptbahnhof"
        dest = "Rotebühlplatz"

        return [
            Journey(
                origin,
                dest,
                dep_time=by - timedelta(minutes=30),
                arr_time=by - timedelta(minutes=15),
            ),
            Journey(
                origin,
                dest,
                dep_time=by - timedelta(minutes=25),
                arr_time=by - timedelta(minutes=10),
            ),
        ]

    def recommend_journey_to_arrive_by(self, journeys, by: dt):
        return journeys[-1]


@Singleton
class MockNotificationHandler(BaseNotificationHandler):
    def set_queue(self, notification_queue: queue.Queue):
        self.notification_queue = notification_queue

    def push(self, notification: Notification):
        if not self.notification_queue:
            raise Exception("no notification queue set")
        self.notification_queue.put(notification)


class TestWorkSession(unittest.TestCase):
    """This use case should best be understood with a flow chart:
    https://preview.tinyurl.com/uvsyfyk
    and a sequence diagram:
    https://preview.tinyurl.com/sdeknxs
    """

    states = {
        "music": "Would you like to listen to music?",
        "music_rec": "How about this Spotify playlist?",
        "project": "Which project do you want to work on?",
        "todos": "tasks",
        "pom_ask": "Do you want to start a pomodoro session?",
        "fin_no_pom": "I hope you'll have a productive session!",
        "pom_start": "I will notify you in",
        "pom_block": "Timer running. I will notify you in",
        "pom_fin": "Good Work! You finished your session.",
        "pom_task": (
            "Say <i>complete</i> to complete the current task."
            "<br>Say <i>switch</i> to switch to a different task."
        ),
        "break_ask": (
            "Do you want to take a <i>break</i>, " "<i>skip</i> it or <i>finish</i>?"
        ),
        "break_start": "I will notify you in",
        "break_block": "Timer running. I will notify you in",
        "break_fin": "Your break is over. Let's get back to work.",
    }

    @classmethod
    def setUpClass(self):
        def setup_scheduler():
            scheduler = BackgroundScheduler()
            scheduler.start()
            return scheduler

        def setup_notification_handler():
            notification_host = "localhost"
            notification_port = 8745
            self.server_url = (
                "http://" + notification_host + ":" + str(notification_port)
            )

            self.notification_queue = queue.Queue()

            notification_handler = MockNotificationHandler.instance()
            notification_handler.set_queue(self.notification_queue)
            return notification_handler

        self.notification_handler = setup_notification_handler()
        self.scheduler = setup_scheduler()

        if "DONOTMOCK" in os.environ:
            purgable_calendar = os.environ["CALDAV_PURGABLE_CALENDAR"]
            self.cal_service = CalService.instance(
                iCloudCaldavRemote.instance(purgable_calendar)
            )
            vvs_service = VVSService.instance(VVSEfaJSONRemote.instance())
            geo_service = GeocodingService.instance(GeocodingJSONRemote.instance())
            todo_service = TodoistService.instance(TodoistJSONRemote.instance())
            music_service = MusicService.instance(SpotifyRemote.instance())
        else:
            self.cal_service = CalService.instance(CalMockRemote.instance())
            vvs_service = MockVVSService.instance()
            geo_service = MockGeocodingService.instance()
            # vvs_service = VVSService.instance(
            #    VVSMockRemote.instance())
            todo_service = TodoistService.instance(TodoistMockRemote.instance())
            music_service = MusicService.instance(MusicMockRemote.instance())

        pref_service = PrefService(MockPrefRemote())

        usecase = WorkSession()
        usecase.set_services(
            pref_service=pref_service,
            cal_service=self.cal_service,
            vvs_service=vvs_service,
            geo_service=geo_service,
            todo_service=todo_service,
            music_service=music_service,
        )

        usecase.set_scheduler(self.scheduler)
        usecase.set_notification_handler(self.notification_handler)

        self.usecase = usecase

    @classmethod
    def setUp(self):
        self.cal_service.purge()
        self.usecase.reset()

    def test_starting_not_worth_it(self):
        event_in_mins = 30
        self.usecase.pref["min_work_period_minutes"] = event_in_mins

        event = Event()
        event.set_start(dt.now(pytz.utc) + timedelta(minutes=event_in_mins - 1))
        event.set_end(event.get_start() + timedelta(minutes=30))
        event.set_title("too soon event")
        self.cal_service.add_event(event)

        reply = self.usecase.advance(None)
        expected = "Your next appointment is too close to start working:"
        self.assertIn(expected, reply.message)
        self.assertIn("too soon event", reply.message)
        self.assertTrue(self.usecase.is_finished())

    @patch.object(LocationHandler._decorated, "get")
    def test_ask_wether_we_can_make_it_there(self, mock_location):
        mock_location.return_value = (48.773466, 9.170824)
        event_in_mins = 30
        self.usecase.pref["min_work_period_minutes"] = event_in_mins

        event = Event()
        event.set_start(dt.now(pytz.utc) + timedelta(minutes=(event_in_mins + 30)))
        event.set_end(event.get_start() + timedelta(minutes=30))
        event.set_title("possibly too soon event")
        self.cal_service.add_event(event)

        reply = self.usecase.advance(None)
        expected = "Your next event does not have a location property"

        self.assertIn(expected, reply.message)
        self.assertIn("possibly too soon event", reply.message)
        self.assertIn("Do you still want to start working?", reply.message)

        reply = self.usecase.advance("yes")
        self.assertIn(self.states["music"], reply.message)

    def test_no_upcoming_events(self):
        reply = self.usecase.advance(None)
        expected = "You have no upcoming events."
        self.assertIn(expected, reply.message)

    @freeze_time("2020-03-14", as_arg=True)
    @patch.object(LocationHandler._decorated, "get")
    @patch.object(TodoistService._decorated, "get_project_names")
    @patch.object(TodoistService._decorated, "get_project_tasks")
    @unittest.skipIf(
        "TRAVIS" in os.environ and "DONOTMOCK" in os.environ,
        "travis IP might be blocked on iCloud",
    )
    def test_creates_reminder_for_upcoming_and_advances(
        frozen_time, self, mock_get_tasks, mock_get_projects, mock_location
    ):

        mock_get_projects.return_value = ["some project"]
        mock_get_tasks.return_value = []

        mock_location.return_value = (48.773466, 9.170824)

        uc = self.usecase

        event = Event()
        event.set_start(dt.now(pytz.utc) + timedelta(minutes=270))
        event.set_end(event.get_start() + timedelta(minutes=30))
        event.set_title("upcoming event")
        event.set_location("Stuttgart Hauptbahnhof")
        self.cal_service.add_event(event)

        reply = uc.advance(None)
        expected = "I created a reminder for when you have to get going to reach:"
        self.assertIn(expected, reply.message)
        self.assertIn("upcoming event", reply.message)
        self.assertIn("<table>", reply.message)
        self.assertIn("Origin", reply.message)

        events = self.cal_service.get_all_events()
        events = list(filter(lambda e: "Hauptbahnhof" in e.get_title(), events))
        self.assertIsNotNone(events)
        journey_event = events[0]
        self.assertIn("From", journey_event.get_title())

        can_work_until = journey_event.get_start() - timedelta(
            minutes=self.usecase.pref["remind_min_before_leaving"]
        )

        # and advances correctly...
        self.assertIn(self.states["music"], reply.message)

        reply = uc.advance('yes')
        self.assertIn(self.states['music_rec'], reply.message)
        self.assertIn("http", reply.message)
        self.assertIn(self.states['project'], reply.message)
        mock_get_projects.assert_called_once()

        reply = uc.advance("some project")
        mock_get_tasks.assert_called_once()
        self.assertIn(self.states["todos"], reply.message)
        self.assertIn(self.states["pom_ask"], reply.message)

        for pomodoro in (False, True):
            with self.subTest("Pomodoro? " + str(pomodoro)):
                if not pomodoro:
                    reply = uc.advance("no")
                    self.assertIn(self.states["fin_no_pom"], reply.message)

                    # starts over...
                    self.assertTrue(uc.is_finished())
                    # does not need to be reset
                    reply = uc.advance(None)
                    self.assertFalse(uc.is_finished())
                else:
                    uc._set_state("pomodoro")
                    for pomodoro_i in range(100):

                        reply = uc.advance("yes")
                        one_pomodoro = timedelta(minutes=25)
                        if dt.now(pytz.utc) + one_pomodoro >= can_work_until:
                            self.assertIn("You should get going", reply.message)
                            self.assertTrue(uc.is_finished())
                            break

                        self.assertIn(self.states["pom_start"], reply.message)

                        self.assertTrue(self.notification_queue.empty())
                        for i in range(10):
                            if not self.notification_queue.empty():
                                break
                            reply = uc.advance("asdfpoijw")
                            self.assertIn(self.states["pom_block"], reply.message)

                        frozen_time.tick(timedelta(minutes=25))

                        # assert notification reached Notification Handler
                        notification = self.notification_queue.get()
                        self.assertTrue(self.notification_queue.empty())
                        self.assertIn(self.states["pom_fin"], notification["title"])
                        self.assertIn(
                            self.states["pom_fin"],
                            notification["options"]["data"]["message"],
                        )

                        self.assertEqual(uc.get_state().lower(), "break")

                        for take_break in (True, False):
                            with self.subTest(
                                str(pomodoro_i) + " Break? " + str(take_break)
                            ):
                                if take_break:
                                    reply = uc.advance("I want to take a break")

                                    one_break = timedelta(minutes=5)
                                    if dt.now(pytz.utc) + one_break >= can_work_until:
                                        self.assertIn(
                                            "You should get going", reply.message
                                        )
                                        self.assertTrue(uc.is_finished())
                                        break

                                    self.assertIn(
                                        self.states["break_start"], reply.message
                                    )

                                    self.assertTrue(self.notification_queue.empty())
                                    for i in range(10):
                                        if not self.notification_queue.empty():
                                            break
                                        reply = uc.advance("asdfpoijw")
                                        self.assertIn(
                                            self.states["break_block"], reply.message
                                        )

                                    frozen_time.tick(timedelta(minutes=5))

                                    # assert notification reached Notification Handler
                                    notification = self.notification_queue.get()
                                    self.assertTrue(self.notification_queue.empty())
                                    self.assertIn(
                                        self.states["break_fin"], notification["title"]
                                    )
                                    self.assertIn(
                                        self.states["break_fin"],
                                        notification["options"]["data"]["message"],
                                    )
                                    self.assertIn(
                                        self.states["pom_ask"],
                                        notification["options"]["data"]["message"],
                                    )
                                else:
                                    uc._set_state("break")
                                    reply = uc.advance("skip")

                        self.assertEqual(uc.get_state().lower(), "pomodoro")

                    # starts over...
                    self.assertTrue(uc.is_finished())
                    # does not need to be reset
                    reply = uc.advance(None)
                    self.assertIn("too close to start working", reply.message)
                    self.assertTrue(uc.is_finished())

    @patch.object(TodoistService._decorated, "get_project_tasks")
    def test_can_cancel_timer(self, get_tasks_mock):
        uc = self.usecase
        uc._set_state("pomodoro")
        uc.chosen_project = "some random project"
        get_tasks_mock.return_value = []

        reply = uc.advance("yes")
        self.assertIn(self.states["pom_start"], reply.message)

        reply = uc.advance("asdf")
        self.assertIn(self.states["pom_block"], reply.message)

        reply = uc.advance("cancel")
        self.assertEqual("", reply.message)

        notification = self.notification_queue.get()
        self.assertTrue(self.notification_queue.empty())
        self.assertIn(self.states["pom_fin"], notification["title"])
        self.assertIn(
            self.states["pom_fin"], notification["options"]["data"]["message"]
        )

        uc._set_state("break")

        reply = uc.advance("break")
        self.assertIn(self.states["break_start"], reply.message)

        reply = uc.advance("asdf")
        self.assertIn(self.states["break_block"], reply.message)
        self.assertIn("Enter <i>cancel</i> to skip forward.", reply.message)

        reply = uc.advance("cancel")
        self.assertIn("", reply.message)

        notification = self.notification_queue.get()
        self.assertTrue(self.notification_queue.empty())
        self.assertIn(self.states["break_fin"], notification["title"])
        self.assertIn(
            self.states["break_fin"], notification["options"]["data"]["message"]
        )
        self.assertIn(
            self.states["pom_ask"], notification["options"]["data"]["message"]
        )

    @patch.object(TodoistService._decorated, "get_project_tasks")
    @patch.object(TodoistService._decorated, "complete_todo")
    @freeze_time("2020-03-14", as_arg=True)
    def test_can_complete_and_switch_tasks(
        frozen_time, self, complete_mock, get_tasks_mock
    ):

        tasks = {"abc": "test todo 1", "def": "test todo 2", "ghi": "test todo 2"}

        def _get_tasks():
            return [
                {"id": k, "content": v, "priority": 0, "due": None}
                for k, v in tasks.items()
            ]

        get_tasks_mock.return_value = _get_tasks()
        uc = self.usecase
        uc._set_state("todo")
        uc.projects = ["some random project"]

        reply = uc.advance("some random project")
        self.assertIn(self.states["todos"], reply.message)
        self.assertIn(self.states["pom_ask"], reply.message)
        self.assertIn("choose a task", reply.message)

        reply = uc.advance("test todo 1")
        self.assertIn("Task chosen: test todo 1", reply.message)
        self.assertIn(self.states["pom_start"], reply.message)
        self.assertIn(self.states["pom_task"], reply.message)

        frozen_time.tick(timedelta(minutes=1))

        reply = uc.advance("asdf")
        self.assertIn(self.states["pom_block"], reply.message)
        self.assertIn(self.states["pom_task"], reply.message)

        del tasks["abc"]
        get_tasks_mock.return_value = _get_tasks()
        reply = uc.advance("complete")
        complete_mock.assert_called_once()
        self.assertEqual(complete_mock.call_args[0][0]["id"], "abc")
        complete_mock.reset_mock()
        self.assertIn(
            "Successfully completed. "
            "Choose a new task, say <i>none</i> or <i>finish</i>.",
            reply.message,
        )
        self.assertIn("<table>", reply.to_html())

        reply = uc.advance("test todo 2")
        self.assertIn("This task is not unique. Choose by ID", reply.message)

        reply = uc.advance("0")  # has to choose by id
        self.assertIn("Switched to test todo 2", reply.message)

        frozen_time.tick(timedelta(minutes=1))

        reply = uc.advance("switch")
        complete_mock.asssert_not_called()
        self.assertIn(
            "Choose a new task, say <i>none</i> or <i>finish</i>.", reply.message
        )
        self.assertIn("<table>", reply.to_html())

        reply = uc.advance("1")
        self.assertIn("Switched to test todo 2", reply.message)

        frozen_time.tick(timedelta(minutes=23))
        notification = self.notification_queue.get()
        self.assertTrue(self.notification_queue.empty())
        self.assertIn(
            self.states["pom_fin"], notification["options"]["data"]["message"]
        )
        self.assertIn(
            "Did you <i>complete</i>", notification["options"]["data"]["message"]
        )

        del tasks["ghi"]
        get_tasks_mock.return_value = _get_tasks()
        reply = uc.advance("yes")
        complete_mock.assert_called_once()
        self.assertEqual(complete_mock.call_args[0][0]["id"], "ghi")
        complete_mock.reset_mock()
        self.assertIn("Successfully completed. ", reply.message)
        self.assertIn(self.states["break_ask"], reply.message)

        reply = uc.advance("skip")
        self.assertIn(self.states["todos"], reply.message)
        self.assertIn(self.states["pom_ask"], reply.message)
        self.assertIn("<table>", reply.to_html())

        reply = uc.advance("test todo 1")
        self.assertIn("I did not get that", reply.message)

        reply = uc.advance("test todo 2")
        self.assertIn("Task chosen: test todo 2", reply.message)
        self.assertIn(self.states["pom_start"], reply.message)
        self.assertIn(self.states["pom_task"], reply.message)

        frozen_time.tick(timedelta(minutes=25))
        notification = self.notification_queue.get()
        self.assertTrue(self.notification_queue.empty())
        self.assertIn(
            self.states["pom_fin"], notification["options"]["data"]["message"]
        )
        self.assertIn(
            "Did you <i>complete</i>", notification["options"]["data"]["message"]
        )

        reply = uc.advance("no")
        self.assertIn(self.states["break_ask"], reply.message)

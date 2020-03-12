import unittest
from urllib.parse import urlparse
from datetime import datetime as dt, timedelta
import pytz

from .. import WorkSession
from services.todoAPI import TodoistService
from services.vvs import VVSService
from services.cal import CalService, Event
#from services.music import MusicService
from services.cal.test import CaldavMockRemote
from services.vvs.test import VVSMockRemote
from services.todoAPI.test import TodoistMockRemote
from services.preferences import PrefService

class TestWorkSession(unittest.TestCase):

    @classmethod
    def setUp(self):
        usecase = WorkSession.instance()

        cal_remote = CaldavMockRemote()
        cal_remote.purge()
        self.cal_service = CalService(cal_remote)

        usecase.set_pref_service(PrefService())
        usecase.set_cal_service(self.cal_service)
        usecase.set_vvs_service(VVSService(VVSMockRemote()))
        usecase.set_todo_service(TodoistService(TodoistMockRemote()))
        #usecase.set_music_service(MusicService(MusicMockRemote()))
        usecase.reset()
        self.usecase = usecase

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
        event['dtstart'] = pytz.utc.localize(dt.now()) + timedelta(minutes=event_in_mins-1)
        event['dtend'] = event['dtstart'] + timedelta(minutes=30)
        event['summary'] = 'too soon event'
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
        event['dtstart'] = pytz.utc.localize(dt.now()) + timedelta(minutes=event_in_mins+30)
        event['dtend'] = event['dtstart'] + timedelta(minutes=30)
        event['summary'] = 'possibly too soon event'
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
            'music': "Do you want music?",
            'music_rec': "How about this Spotify playlist?",

            'project': "Which project do you want to work on?",
            'todos': "Here are your Todo's:",
            'which_todo': "Which todo do you want to work on?",

            'pomodoro': "Do you want to start a pomodoro session?",
            'fin_no_pom': "I wish you a productive session!",

            'pom_start': "Pomodoro timer started. I will notify you in",
            'pom_block': "left in your pomodoro session. Stay focused.",
            'pom_fin': "Great Work! Your pomodoro session is finished. "
                    + "Do you want to keep working, take a break or stop altogether?",

            'break_start': "Break timer started. I will notify you in",
            'break_block': "left in your break. Relax.",
            'break_fin': "Your break is over. Let's get back to work. "
        }

        # TODO
        return

        uc = self.usecase

        reply = uc.advance(None)
        self.assertIn(states['rem_music'], reply.message)

        reply = uc.advance({'message': 'yes'})
        self.assertIn(states['music_rec'], reply.message)
        self.assertNotNone(reply.link)
        self.assertTrue(self.uri_valid(reply.link))
        self.assertIn(states['project'], reply.message)
        self.assertNotNone(reply.list) # list of projects

        reply = uc.advance({'message': 'Software Engineering'})
        self.assertIn(states['todos'], reply.message)
        self.assertNotNone(reply.list)
        self.assertTrue(len(reply.list) > 0)
        self.assertIn(states['which_todo'], reply.message)

        reply = uc.advance({'message': 'Test Hello'})
        self.assertIn(states['pomodoro'], reply.message)

        for pomodoro in (True, False):
            with self.subTest('Pomodoro? '+str(pomodoro)):
                if not pomodoro:
                    reply = uc.advance({'message': 'no'})
                    self.assertIn(states['fin_no_pom'], reply.message)
                    self.assertTrue(uc.is_finished())
                else:
                    for i in range(0, 5):
                        #TODO set pomodoro limit
                        reply = uc.advance({'message': 'yes'})
                        self.assertIn(states['pom_start'], reply.message)
                        # before finish yields nothing
                        for i in range(1,10):
                            reply = uc.advance({'message': 'asdfpoijw'})
                            self.assertIn(states['pom_block'], reply.message)

                        uc.finish_pomodoro()
                        #TODO assert notification reached Notification Handler
                        # or some sort of inbox? should contain pomodoro_fin
                        self.assertEqual(uc.get_state(), "pomodoro_fin")

                        for take_break in (True, False):
                            with self.subTest('Break? '+str(take_break)):
                                if take_break:
                                    reply = uc.advance({'message': 'I want to take a break'})
                                    self.assertIn(states['break_start'], reply.message)

                                    for i in range(1,10):
                                        reply = uc.advance({'message': 'asdfpoijw'})
                                        self.assertIn(states['break_block'], reply.message)

                                    uc.finish_break()
                                    #TODO assert notification reached Notification Handler
                                    # or some sort of inbox? should contain break_fin
                                    self.assertEqual(uc.get_state(), "break_fin")
                                else:
                                    reply = uc.advance({'message': 'Keep working'})

                        #TODO should also ask for which project to work on
                        #reply = reply || notification
                        #self.assertIn(states['which_project'], notification.message)
                        self.assertIn(states['project'], reply.message)
                        self.assertNotNone(reply.list) # list of projects

                        reply = uc.advance({'message': 'Software Engineering'})
                        self.assertIn(states['todos'], reply.message)
                        self.assertNotNone(reply.list)
                        self.assertTrue(len(reply.list) > 0)
                        self.assertIn(states['which_todo'], reply.message)

                        reply = uc.advance({'message': 'Test Hello'})
                        self.assertIn(states['pomodoro'], reply.message)

                    # finally no more pomodoros...
                    reply = uc.advance({'message': 'no'})
                    self.assertIn(states['fin_no_pom'], reply.message)
                    self.assertTrue(uc.is_finished())

                # starts over...
                reply = uc.advance(None)
                self.assertIn(states['rem_music'], reply.message)

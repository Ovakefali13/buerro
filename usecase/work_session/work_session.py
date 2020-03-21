from datetime import datetime as dt, timedelta
import pytz
import re


from services import TodoistService, VVSService, CalService, PrefService, MusicService
from usecase import Usecase, Reply, StateMachine, FinishedException
#from usecase import TransportUsecase
from handler import NotificationHandler

class WorkSession(Usecase):
    """This use case should best be understood with a flow chart:
    https://preview.tinyurl.com/uvsyfyk
    """

    def __init__(self):

        self.fsm = StateMachine()
        self.define_state_transitions()

        self.scheduler = None
        self.notification_handler = NotificationHandler.instance()

    def set_services(self,
                    pref_service:PrefService,
                    cal_service:CalService,
                    vvs_service:VVSService,
                    todo_service:TodoistService,
                    music_service:MusicService):
        # TODO self.transport_usecase = None

        self.pref_service = pref_service
        self.pref = pref_service.get_preferences('work_session')
        self.cal_service = cal_service
        self.vvs_service = vvs_service
        self.todo_service = todo_service
        self.music_service = music_service

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler
    def set_notification_handler(self, handler):
        self.notification_handler = handler

    def reset(self):
        self.fsm.reset()

    def advance(self, message):
        if not self.cal_service:
            raise Exception("Set Services!")
        if not isinstance(message, str) and message is not None:
            raise Exception("wrong data type for message passed: "
                    +str(type(message)))
        try:
            reply = self.fsm.advance(message)
        except FinishedException:
            self.reset()
            reply = self.fsm.advance(message)
        return Reply(reply)

    def is_finished(self):
        return self.fsm.is_finished()

    def _set_state(self, state:str):
        self.fsm._set_state(state)
    def get_state(self):
        return self.fsm.currentState

    def wake_up(self, reply, next_state):
        self.expireBy = None
        self._set_state(next_state)
        self.notification_handler.push(reply.to_notification())

    def wait_until(self, when:dt, reply, next_state):
        if not self.scheduler:
            raise Exception("Scheduler not set in use case")

        self.expire_by = when
        self.scheduler.add_job(func=self.wake_up,
                                trigger='date', run_date=when,
                                args=(reply, next_state))

    def define_state_transitions(self):
        def find_whole_word(w):
            return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

        def start_trans(message):
            def _event_too_close(event, journey=None):
                msg = "Your next appointment is too close to start working: \n"
                msg += event.summarize()
                if journey:
                    msg += "\nThe recommended journey: \n"
                    msg += str(journey)
                next_state = "end_state"
                return next_state, msg

            def _event_possibly_too_close(event):
                msg = "Your next appointment might be too close to start working:\n"
                msg += event.summarize()
                msg += "\nDo you still want to start working?"
                return "end_state", msg

            next_events = self.cal_service.get_next_events()
            if next_events:
                next_event = next_events[0]
                now = pytz.utc.localize(dt.now())
                minutes_until = (next_event['dtstart'].dt - now).seconds / 60
                min_work_period = self.pref['min_work_period_minutes']
                if minutes_until < min_work_period:
                    return _event_too_close(next_event)

                if not 'location' in next_event:
                    if minutes_until < 120:
                        return _event_possibly_too_close(next_event)
                else:
                    origin = "Rotebühlplatz" # TODO determine current location
                    dest = next_event['location']

                    origin_id = self.vvs_service.get_location_id(origin)
                    dest_id = self.vvs_service.get_location_id(dest)
                    if not origin_id or not dest_id:
                        return _event_possibly_too_close(next_event)

                    min_early = self.pref['be_minutes_early']
                    arrive_by = next_event['dtstart'].dt - timedelta(minutes=min_early)

                    journeys = self.vvs_service.get_journeys_for_id(
                        origin_id, dest_id, "arr", arrive_by)
                    journey = self.vvs_service.recommend_journey_to_arrive_by(journeys,
                        next_event.get_start())

                    now = pytz.utc.localize(dt.now())
                    minutes_until = (journey.dep_time - now).seconds / 60
                    if minutes_until < min_work_period:
                        return _event_too_close(next_event, journey)

                    journey_event = journey.to_event()
                    reminder = self.pref['remind_min_before_leaving']
                    journey_event.set_reminder(timedelta(minutes=reminder))
                    self.cal_service.add_event(journey_event)

                    # TODO create notification
                    msg = "I created a reminder for when you have to get going to reach:\n"
                    msg += next_event.summarize()
                    msg += "\n using this VVS journey:\n"
                    msg += str(journey)
                    msg += '\nWould you like to listen to music?'

                    return "music", msg
            else:
                msg = 'You have no upcoming events.'
                msg += '\nWould you like to listen to music?'
                return "music", msg

        def music_trans(message):
            msg =""
            reply = {}
            if find_whole_word('yes')(message):
                link = self.music_service.get_playlist_for_mood('focus')
                msg += "How about this Spotify playlist?"
                reply = {**reply, 'link': link}

            msg += "\nWhich project do you want to work on?\n"
            self.projects = self.todo_service.get_project_names()
            msg += str(self.projects)
            reply = {**reply, 'message': msg}
            return "todo", reply

        def todo_trans(message):
            for project in self.projects:
                if project.lower() in message.lower():
                    self.chosen_project = project
                    break
            else:
                msg = ( "I could not match your answer to any of your projects. "
                        "Would you repeat that, please?")
                return "todo", msg

            todos = self.todo_service.get_project_items(self.chosen_project)
            reply = {'list': todos}
            msg = f"Here are your Todo's for {self.chosen_project}."
            msg += "\nDo you want to start a pomodoro session?"
            return "pomodoro", {**reply, 'message': msg}

        def pomodoro_trans(message):
            if message is None: message = ""
            if find_whole_word('no')(message):
                return "end_state", "I hope you'll have a productive session!"
            elif find_whole_word('yes')(message):
                minutes = self.pref['pomodoro_minutes']
                self.wait_until(when=dt.now() + timedelta(minutes=minutes),
                    next_state="break",
                    reply=Reply(("Good Work! You finished your session."
                            "\nDo you want to take a break, skip it or finish?"))
                )
                return "wait_state", f"I will notify you in {minutes} minutes."
            else:
                msg = ( "I did not get that. "
                        "Please answer with yes or no.")
                return "pomodoro", msg

        def break_trans(message):
            if message is None: message = ""
            if find_whole_word('skip')(message):
                """
                minutes = self.pref['pomodoro_minutes']
                self.wait_until(when=dt.now() + timedelta(minutes=minutes),
                    next_state="break",
                    reply=Reply(("Good Work! You finished your session."
                            "\nDo you want to take a break, skip it or finish?"))
                )
                return "wait_state", f"I will notify you in {minutes} minutes."
                """
                return "pomodoro", f"Do you want to start another pomodoro?"
            elif find_whole_word('finish')(message):
                return "end_state", "Okay let's finish up. See you."
            elif find_whole_word('break')(message):
                minutes = self.pref['break_minutes']
                self.wait_until(when=dt.now() + timedelta(minutes=minutes),
                    next_state="pomodoro",
                    reply=Reply(("Your break is over."
                                " Do you want to get back to work?"))
                )
                return "wait_state", f"I will notify you in {minutes} minutes."
            else:
                msg = ("I did not get that. "
                        "Please answer with (break, skip or finish).")
                return "pomodoro", msg

        def wait_trans(message):
            if self.expire_by:
                period = self.expire_by - dt.now()
                minutes, seconds = divmod(period.seconds, 60)
                msg = (  "Timer running."
                        f"I will notify you in {minutes}:{seconds}." )
                return "wait_state", msg
            else:
                raise Exception("in wait_state even though timer expired")

        m = self.fsm
        m.add_state("start", start_trans)
        m.set_start("start")
        m.add_state("music", music_trans)
        m.add_state("todo", todo_trans)
        m.add_state("pomodoro", pomodoro_trans)
        m.add_state("break", break_trans)
        m.add_state("wait_state", wait_trans)
        m.add_state("error_state", None, end_state=True)
        m.add_state("end_state", None, end_state=True)

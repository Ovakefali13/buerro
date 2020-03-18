from datetime import datetime as dt, timedelta
import pytz

from usecase import Usecase, Reply, StateMachine
from services.singleton import Singleton
from services.todoAPI import TodoistService
from services.vvs import VVSService
from services.cal import CalService
from services.preferences import PrefService
from services.music import MusicService
#from usecase import TransportUsecase

@Singleton
class WorkSession(Usecase):
    """This use case should best be understood with a flow chart:
    https://preview.tinyurl.com/uvsyfyk
    """

    def __init__(self):
        super().__init__()

        self.cal_service = CalService.instance()
        self.vvs_service = VVSService.instance()
        self.todo_service = TodoistService.instance()
        self.music_service = MusicService.instance()
        self.pref = PrefService()
        # TODO self.transport_usecase = None

        self.fsm = StateMachine()
        self.define_state_transitions()

    def set_pref_service(self, service:PrefService):
        self.prefService = service
        self.pref = service.get_preferences('work_session')

    def set_cal_service(self, service:CalService):
        self.cal_service = service
    def set_vvs_service(self, service:VVSService):
        self.vvs_service = service
    def set_todo_service(self, service:TodoistService):
        self.todo_service = service
    def set_music_service(self, service:MusicService):
        self.music_service = service

    def reset(self):
        self.fsm.reset()

    def advance(self, message):
        if not isinstance(message, str) and message is not None:
            raise Exception("wrong data type for message passed: "
                    +str(type(message)))
        return Reply(self.fsm.advance(message))

    def is_finished(self):
        return self.fsm.finished

    def define_state_transitions(self):
        def start_trans(message):
            def _event_too_close(event, journey=None):
                msg = "Your next appointment is too close to start working: \n"
                msg += event.summarize()
                if journey:
                    msg += "\nThe recommended journey: \n"
                    msg += str(journey)
                next_state = "end_state"
                return next_state, {'message': msg}

            def _event_possibly_too_close(event):
                msg = "Your next appointment might be too close to start working:\n"
                msg += event.summarize()
                msg += "\nDo you still want to start working?"
                return "end_state", {'message': msg}

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

                    return "music", {'message': msg}
            else:
                msg = 'You have no upcoming events.'
                msg += '\nWould you like to listen to music?'
                return "music", {'message': msg}

        def music_trans(message):
            msg =""
            reply = {}
            if 'yes' in message:
                link = self.music_service.get_playlist_for_mood('focus')
                msg += "How about this Spotify playlist?"
                reply = {**reply, 'link': link}

            msg += "\nWhich project do you want to work on?\n"
            self.projects = self.todo_service.get_project_names()
            msg += str(self.projects)
            reply = {**reply, 'message': msg}
            return "todo", reply

        def todo_trans(message):
            return "end_state", None

        m = self.fsm
        m.add_state("start", start_trans)
        m.set_start("start")
        m.add_state("music", music_trans)
        m.add_state("todo", todo_trans)
        m.add_state("error_state", None, end_state=True)
        m.add_state("end_state", None, end_state=True)

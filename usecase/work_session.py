from datetime import datetime as dt
import pytz

from usecase import Usecase, Reply, StateMachine
from services.singleton import Singleton
from services.todoAPI import TodoistService
from services.vvs import VVSService
from services.cal import CalService
from services.preferences import PrefService
#from services.music import MusicService
#from usecase import TransportUsecase

@Singleton
class WorkSession(Usecase):

    def __init__(self):
        super().__init__()

        self.calService = None
        self.vvsService = None
        # TODO self.transportUsecase = None
        self.todoService = None
        # self.musicService = None
        self.pref = None

        self.fsm = StateMachine()
        self.define_state_transitions()

    def set_pref_service(self, service:PrefService):
        self.prefService = service
        self.pref = service.get_preferences('work_session')

    def set_cal_service(self, service:CalService):
        self.calService = service
    def set_vvs_service(self, service:VVSService):
        self.vvsService = service
    def set_todo_service(self, service:TodoistService):
        self.todoService = service

    def reset(self):
        self.fsm.reset()

    def advance(self, data):
        return Reply(self.fsm.advance(data))

    def is_finished(self):
        return self.fsm.finished

    def recommend_journey_to_event(self, journeys, event):
        def _time_from_event(journey, event):
            event_buffer = timedelta(minutes=self.pref['be_minutes_early'])
            event_dt = event['dtstart'].dt
            return (event_dt - event_buffer) - journey.get_arr_time()

        """ three requirements for choosing a tram:
                1. I am on time
                2. I am not there too early (just on time)
                3. It doesn't take too long (advantage over others > 5 minutes)
            solution:
                1. filter such that none are too late
                2. sort in reverse order (latest to earliest)
                3. only consider ealier ones if they take significantly less time
        """
        none_too_late = list(filter(lambda journey:
            _time_from_event(journey, event) >= timedelta(0), journeys))
        sorted_by_arrival = sorted(none_too_late, reverse=True,
                key=lambda journey : journey.get_arr_time())

        recommended_journey = sorted_by_arrival[0]
        that_much_faster = 5
        for journey in sorted_by_arrival:
            if(recommended_journey.get_duration() >= that_much_faster + journey.get_duration()):
                recommended_journey = journey

    def define_state_transitions(self):
        def start_trans(data):
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

            next_events = self.calService.get_next_events()
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
                    origin = "Hauptbahnhof Stuttgart" # TODO determine current location
                    dest = next_event['location'] # TODO for sure that it's valid?
                    min_early = self.pref['be_minutes_early']
                    arrive_by = next_event['dtstart'].dt - timedelta(minutes=min_early)
                    journeys = self.vvsService.get_journeys(origin, dest,
                        "arr", arrive_by)
                    journey = self.recommend_journey_to_event(journey, next_event)

                    now = pytz.utc.localize(dt.now())
                    minutes_until = (journey.dep_time - now).seconds / 60
                    if minutes_until < min_work_period:
                        return _event_too_close(next_event, journey)
            else:
                msg = 'You have no upcoming events.'
                return "next_state", {'message': msg}

            return

        m = self.fsm
        m.add_state("start", start_trans)
        m.set_start("start")
        m.add_state("error_state", None, end_state=True)
        m.add_state("end_state", None, end_state=True)

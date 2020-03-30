from datetime import datetime as dt, timedelta
import pytz
import re
from util import link_to_html, list_to_html, dict_to_html, table_to_html


from services import TodoistService, VVSService, CalService, PrefService, MusicService
from usecase import Usecase, Reply, StateMachine, FinishedException
#from usecase import TransportUsecase
from handler import NotificationHandler

class NonUniqueTaskException(Exception):
    pass

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
        self.pref = self.pref_service.get_preferences('work_session')
        self.cal_service = cal_service
        self.vvs_service = vvs_service
        self.todo_service = todo_service
        self.music_service = music_service

    def set_default_services(self):
        self.pref_service = PrefService()
        self.pref = self.pref_service.get_preferences('work_session')
        self.cal_service = CalService.instance()
        self.vvs_service = VVSService.instance()
        self.todo_service = TodoistService.instance()
        self.music_service = MusicService.instance()

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler
    def set_notification_handler(self, handler):
        self.notification_handler = handler

    def reset(self):
        self.fsm.reset()

    def advance(self, message):
        if not hasattr(self, 'cal_service'):
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

    def update_todos(self):
        self.todos = self.todo_service.get_project_tasks(self.chosen_project)
        self.todos = {e['id']: e for e in self.todos}
        self.todo_dict = {id: v['content'] for id, v in self.todos.items()}

    def wake_up(self, reply, next_state):
        self.expire_by = None
        self.wake_job = None
        self._set_state(next_state)
        self.notification_handler.push(reply.to_notification())

    def wait_until(self, when:dt, reply, next_state):
        if not self.scheduler:
            raise Exception("Scheduler not set in use case")

        self.expire_by = when
        self.wake_job = self.scheduler.add_job(func=self.wake_up,
                                trigger='date', run_date=when,
                                args=(reply, next_state))

    def enough_time_for(self, delta:timedelta):
        if hasattr(self, 'journey'):
            leave_buffer = timedelta(minutes=self.pref['remind_min_before_leaving'])
            get_going_by = (self.journey.dep_time - leave_buffer)
            end = dt.now(pytz.utc) + delta
            if end >= get_going_by:
               return False
            return True
        return True

    def define_state_transitions(self):
        def find_whole_word(w):
            return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

        def start_trans(message):
            def _event_too_close(event, journey=None):
                msg = "Your next appointment is too close to start working: <br>"
                msg += event.summarize()
                if journey:
                    msg += "<br>The recommended journey: <br>"
                    msg += str(journey)
                next_state = "end_state"
                return next_state, msg

            def _event_possibly_too_close(event):
                msg = "Your next appointment might be too close to start working:<br>"
                msg += event.summarize()
                msg += "<br>Do you still want to start working?"
                return "end_state", msg

            next_events = self.cal_service.get_next_events()
            if next_events:
                next_event = next_events[0]
                now = dt.now(pytz.utc)
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

                    journey = None
                    try:
                        origin_id = self.vvs_service.get_location_id(origin)
                        dest_id = self.vvs_service.get_location_id(dest)

                        min_early = self.pref['be_minutes_early']
                        arrive_by = next_event['dtstart'].dt - timedelta(minutes=min_early)

                        journeys = self.vvs_service.get_journeys_for_id(
                            origin_id, dest_id, "arr", arrive_by)
                        journey = self.vvs_service.recommend_journey_to_arrive_by(journeys,
                            next_event.get_start())
                    except:
                        # could not determine next location
                        return _event_possibly_too_close(next_event)


                    now = dt.now(pytz.utc)
                    minutes_until = (journey.dep_time - now).seconds / 60
                    if minutes_until < min_work_period:
                        return _event_too_close(next_event, journey)

                    self.journey = journey
                    journey_event = journey.to_event()
                    self.cal_service.add_event(journey_event)

                    msg = "I created a reminder for when you have to get going to reach:<br>"
                    msg += next_event.summarize()
                    msg += "<br> using this VVS journey:<br>"
                    msg += table_to_html(journey.to_table())
                    msg += '<br>Would you like to listen to music?'

                    return "music", msg

            msg = 'You have no upcoming events.'
            msg += '<br>Would you like to listen to music?'
            return "music", msg

        def music_trans(message):
            msg =""
            reply = {}
            if find_whole_word('yes')(message):
                link, name = self.music_service.get_playlist_for_mood('focus')
                msg += "How about this Spotify playlist?"
                msg += "<br>" + link_to_html(link, altname=name) + "<br>"

            msg += "<br>Which project do you want to work on?<br>"
            self.projects = self.todo_service.get_project_names()
            reply = {**reply, 'message': msg, 'list': self.projects}
            return "todo", reply

        def get_todos_and_ask_for_pomodoro():
            try:
                self.update_todos()
            except Exception as e:
                print("Failed to fetch todos: ", e)
                msg = "Failed to fetch todos.<br>"
            if self.todo_dict:
                msg = f"Here are your tasks for {self.chosen_project}: <br>"
                msg += dict_to_html(self.todo_dict) + "<br>"
            else:
                msg = f"There are no Todo's for {self.chosen_project}.<br>"

            msg += "<br>Do you want to start a pomodoro session?"
            msg += "<br>Then say <i>yes</i> or choose a task."
            return "pomodoro", msg

        def todo_trans(message):
            for project in self.projects:
                if project.lower() in message.lower():
                    self.chosen_project = project
                    break
            else:
                msg = ( "I could not match your answer to any of your projects. "
                        "Would you repeat that, please?")
                return "todo", msg

            return get_todos_and_ask_for_pomodoro()

        def set_chosen_task(message):
            if self.todo_dict:
                for key in self.todo_dict.keys():
                    if key in message:
                        self.chosen_task = self.todos[key]
                        break
                else:
                    for key, name in self.todo_dict.items():
                        if name in message:
                            if not self.chosen_task:
                                self.chosen_task = self.todos[key]
                            else:
                                raise NonUniqueTaskException("This task is not unique.")


        def ask_for_break():
            return ("Good Work! You finished your session."
                    "<br>Do you want to take a <i>break</i>, "
                    "<i>skip</i> it or <i>finish</i>?")

        def ask_for_task_state():
            return ('Say <i>complete</i> to complete the current task.<br>'
                    'Say <i>switch</i> to switch to a different task.')

        def pomodoro_trans(message):
            self.chosen_task = None
            msg = ""
            if message is None: message = ""
            if find_whole_word('no')(message):
                return "end_state", "I hope you'll have a productive session!"
            elif find_whole_word('yes')(message):
                next_state = 'break'
                wake_up_reply = Reply(ask_for_break())
            else:
                try:
                    set_chosen_task(message)
                except NonUniqueTaskException:
                    return "pomodoro", "This task is not unique. Choose by ID."

                if self.chosen_task:
                    msg += f"Task chosen: {self.chosen_task['content']}.<br>"
                    next_state = "pom_review"
                    wake_up_reply = Reply("Good Work! You finished your session."
                                    "<br>Did you <i>complete</i> your task?")
                else:
                    msg = ( "I did not get that. "
                            "Please answer with yes, no, a task name or a task id.")
                    return "pomodoro", msg

            minutes = self.pref['pomodoro_minutes']
            delta = timedelta(minutes=minutes)

            if not self.enough_time_for(delta):
                msg =   ("Can't start another pomodoro. "
                         "You should get going on your journey. <br>")
                return "end_state", {'message': msg,
                                     'table': self.journey.to_table() }

            self.wait_until(when=dt.now(pytz.utc) + delta,
                next_state=next_state,
                reply=wake_up_reply
            )

            msg += f"I will notify you in {minutes} minutes.<br>"
            if self.chosen_task:
                msg += ask_for_task_state()

            return "wait_state", msg

        def pom_review_trans(message):
            msg = ""
            if find_whole_word('complete')(message):
                try:
                    self.todo_service.complete_todo(self.chosen_task)
                    msg += "Successfully completed. "
                    self.update_todos()
                except Exception as e:
                    print("Could not complete the task: ", e)
                    msg += "Failed to commit the complete. "
            else:
                msg += ask_for_break()
                return "break", msg

        def break_trans(message):
            if message is None: message = ""
            if find_whole_word('skip')(message):
                return get_todos_and_ask_for_pomodoro()
            elif find_whole_word('finish')(message):
                return "end_state", "Okay let's finish up. See you."
            elif find_whole_word('break')(message):
                minutes = self.pref['break_minutes']
                delta = timedelta(minutes=minutes)

                if not self.enough_time_for(delta):
                    msg =   ("Can't start another break."
                             "You should get going on your journey. <br>")
                    return "end_state", {'message': msg,
                                         'table': self.journey.to_table() }

                self.wait_until(when=dt.now(pytz.utc) + delta,
                    next_state="pomodoro",
                    reply=Reply(("Your break is over."
                                " Do you want to get back to work?"))
                )
                return "wait_state", f"I will notify you in {minutes} minutes."
            else:
                msg = ("I did not get that. "
                        "Please answer with (break, skip or finish).")
                return "pomodoro", msg

        def choosing_todo_trans(message):
            self.chosen_task = None
            if 'none' == message.lower():
                return "wait_state", "No task chosen."
            else:
                try:
                    set_chosen_task(message)
                except NonUniqueTaskException:
                    return "choosing_todo", "This task is not unique. Choose by ID."

                if self.chosen_task:
                    self.choosing = False
                    return "wait_state", f"Switched to {self.chosen_task['content']}."
                else:
                    msg = "I could not match that to any task."
                    return "wait_state", msg

        def wait_trans(message):
            if not self.expire_by and self.wake_job:
                raise Exception("in wait_state even though timer expired")

            msg = ""
            if find_whole_word('cancel')(message):
                self.wake_job.remove()

                func = self.wake_job.func
                args = self.wake_job.args
                kwargs = self.wake_job.kwargs
                func(*args, **kwargs)
                return "wait_state", "Cancelled interval."

            elif self.chosen_task and find_whole_word('complete')(message):
                try:
                    self.todo_service.complete_todo(self.chosen_task)
                    msg += "Successfully completed. "
                    self.update_todos()
                except Exception as e:
                    print("Could not complete the task: ", e)
                    msg += "Failed to commit the complete. "

                if self.todo_dict:
                    msg += "Choose a new task, say <i>none</i> or finish."
                return "choosing_todo", {'message': msg, 'dict': self.todo_dict}

            else:
                period = self.expire_by - dt.now(pytz.utc)
                minutes, seconds = divmod(period.seconds, 60)
                msg = (  "Timer running. "
                        f"I will notify you in {minutes}:{seconds}. "
                         "Enter <i>cancel</i> to skip forward.")
                if self.chosen_task:
                    msg += ask_for_task_state()
                return "wait_state", msg

        m = self.fsm
        m.add_state("start", start_trans)
        m.set_start("start")
        m.add_state("music", music_trans)
        m.add_state("todo", todo_trans)
        m.add_state("pomodoro", pomodoro_trans)
        m.add_state("pom_review", pom_review_trans)
        m.add_state("break", break_trans)
        m.add_state("wait_state", wait_trans)
        m.add_state("choosing_todo", choosing_todo_trans)
        m.add_state("error_state", None, end_state=True)
        m.add_state("end_state", None, end_state=True)

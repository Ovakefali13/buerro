from datetime import datetime as dt, timedelta
import re
import pytz

from util import link_to_html, table_to_html
from services import (
    TodoistService,
    VVSService,
    GeocodingService,
    CalService,
    PrefService,
    MusicService,
)
from usecase import Usecase, Reply, StateMachine, FinishedException
# from usecase import TransportUsecase
from handler import NotificationHandler, LocationHandler


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

        self.pref_service = None
        self.pref = None
        self.cal_service = None
        self.vvs_service = None
        self.geo_service = None
        self.todo_service = None
        self.music_service = None

        self.journey = None
        self.projects = []
        self.chosen_project = None
        self.todos = []
        self.chosen_task = None
        self.choosing = False
        self.todo_table = {}

        self.expire_by = None
        self.wake_job = None

    def set_services(
        self,
        pref_service: PrefService,
        cal_service: CalService,
        vvs_service: VVSService,
        geo_service: GeocodingService,
        todo_service: TodoistService,
        music_service: MusicService,
    ):
        # TODO self.transport_usecase = None

        self.pref_service = pref_service
        self.pref = self.pref_service.get_preferences("work_session")
        self.cal_service = cal_service
        self.vvs_service = vvs_service
        self.geo_service = geo_service
        self.todo_service = todo_service
        self.music_service = music_service

    def set_default_services(self):
        self.pref_service = PrefService()
        self.pref = self.pref_service.get_preferences("work_session")
        self.cal_service = CalService.instance()
        self.vvs_service = VVSService.instance()
        self.geo_service = GeocodingService.instance()
        self.todo_service = TodoistService.instance()
        self.music_service = MusicService.instance()

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler

    def set_notification_handler(self, handler):
        self.notification_handler = handler

    def reset(self):
        self.fsm.reset()

    def advance(self, message):
        if not hasattr(self, "cal_service"):
            raise Exception("Set Services!")
        if not isinstance(message, str) and message is not None:
            raise Exception("wrong data type for message passed: " + str(type(message)))
        try:
            reply = self.fsm.advance(message)
        except FinishedException:
            self.reset()
            reply = self.fsm.advance(message)
        return Reply(reply)

    def is_finished(self):
        return self.fsm.is_finished()

    def _set_state(self, state: str):
        self.fsm._set_state(state) # pylint: disable=protected-access

    def get_state(self):
        return self.fsm.currentState

    def update_todos(self):
        todos = self.todo_service.get_project_tasks(self.chosen_project)
        todo_table = self.todo_service.tasks_as_table(todos)

        self.todos = {str(i): e for i, e in enumerate(todos)}
        self.todo_table = {"ID": self.todos.keys(), **todo_table}

    def wake_up(self, reply, next_state):
        self.notification_handler.push(reply.to_notification())
        self.expire_by = None
        self._set_state(next_state)

    def wait_until(self, when: dt, reply, next_state):
        if not self.scheduler:
            raise Exception("Scheduler not set in use case")

        self.expire_by = when
        self.wake_job = self.scheduler.add_job(
            func=self.wake_up, trigger="date", run_date=when, args=(reply, next_state)
        )

    def enough_time_for(self, delta: timedelta):
        if hasattr(self, "journey") and self.journey:
            leave_buffer = timedelta(minutes=self.pref["remind_min_before_leaving"])
            get_going_by = self.journey.dep_time - leave_buffer
            end = dt.now(pytz.utc) + delta
            if end >= get_going_by:
                return False
            return True
        return True

    def define_state_transitions(self): # pylint: disable=too-many-locals,too-many-statements
        def find_whole_word(w):
            return re.compile(r"\b({0})\b".format(w), flags=re.IGNORECASE).search

        def start_trans(message): # pylint: disable=unused-argument
            def _event_too_close(event, journey=None):
                msg = "Your next appointment is too close to start working: <br>"
                msg += event.summarize()
                if journey:
                    msg += "<br>The recommended journey: <br>"
                    msg += str(journey)
                next_state = "end_state"
                return next_state, msg

            def _no_journey(event):
                if not "location" in event:
                    msg = "Your next event does not have a location property:<br>"
                else:
                    msg = (
                        "I could not determine a journey "
                        "to get to your next event:<br>"
                    )

                msg += event.summarize()
                msg += "<br>Do you still want to start working?"
                return "no_journey", msg

            def _get_journey_to(event):
                location = LocationHandler.instance().get()
                origin = self.geo_service.get_address_from_coords(location)

                dest = event["location"]

                journey = None
                origin_id = self.vvs_service.get_location_id(origin)
                dest_id = self.vvs_service.get_location_id(dest)

                min_early = self.pref["be_minutes_early"]
                arrive_by = event["dtstart"].dt - timedelta(
                    minutes=min_early
                )

                journeys = self.vvs_service.get_journeys_for_id(
                    origin_id, dest_id, "arr", arrive_by
                )
                journey = self.vvs_service.recommend_journey_to_arrive_by(
                    journeys, event.get_start()
                )
                return journey


            now = dt.now(pytz.utc)
            next_events = self.cal_service.get_events_between(
                start=now,
                end=now + timedelta(hours=8)
            )

            if not next_events:
                msg = "You have no upcoming events."
                msg += "<br>Would you like to listen to music?"
                return "music", msg

            next_event = next_events[0]

            minutes_until = (next_event["dtstart"].dt - now).seconds / 60
            min_work_period = self.pref["min_work_period_minutes"]
            if minutes_until < min_work_period:
                return _event_too_close(next_event)

            if not "location" in next_event:
                return _no_journey(next_event)

            self.journey = _get_journey_to(next_event)

            minutes_until = (self.journey.dep_time - now).seconds / 60
            if minutes_until < min_work_period:
                return _event_too_close(next_event, self.journey)

            journey_event = self.journey.to_event()
            self.cal_service.add_event(journey_event)

            msg = "I created a reminder for when you have to get going to reach:<br>"
            msg += next_event.summarize()
            msg += "<br> using this VVS journey:<br>"
            msg += table_to_html(self.journey.to_table())
            msg += "<br>Would you like to listen to music?"

            return "music", msg


        def no_journey_trans(message):
            if find_whole_word("yes")(message):
                return "music", "Would you like to listen to music?"
            if find_whole_word("no")(message):
                return "end_state", "Alright. See you soon!"
            return (
                "no_journey",
                ("I did not get that, please answer with yes or no"),
            )

        def music_trans(message):
            msg = ""
            reply = {}
            if find_whole_word("yes")(message):
                link, name = self.music_service.get_playlist_for_mood("focus")
                msg += "How about this Spotify playlist?"
                msg += "<br>" + link_to_html(link, altname=name) + "<br><br>"

            msg += "Which project do you want to work on?<br>"
            self.projects = self.todo_service.get_project_names()
            reply = {**reply, "message": msg, "list": self.projects}
            return "todo", reply

        def get_ask_for_pomodoro_msg():
            self.update_todos()
            if self.todo_table:
                msg = f"Here are your tasks for {self.chosen_project}: <br>"
                msg += table_to_html(self.todo_table) + "<br>"
            else:
                msg = f"There are no Todo's for {self.chosen_project}.<br>"

            msg += "<br>Do you want to start a pomodoro session?"
            if self.todo_table:
                msg += "<br>Then say <i>yes</i> or choose a task."
            return msg

        def todo_trans(message):
            for project in self.projects:
                if project.lower() in message.lower():
                    self.chosen_project = project
                    break
            else:
                msg = (
                    "I could not match your answer to any of your projects. "
                    "Would you repeat that, please?"
                )
                return "todo", msg

            return "pomodoro", get_ask_for_pomodoro_msg()

        def set_chosen_task(message):
            if self.todo_table:
                if message in self.todos:
                    self.chosen_task = self.todos[message]
                else:
                    for todo in self.todos.values():
                        if todo["content"] in message:
                            if not self.chosen_task:
                                self.chosen_task = todo
                            else:
                                raise NonUniqueTaskException("This task is not unique.")

        def ask_for_break():
            return (
                "Do you want to take a <i>break</i>, "
                "<i>skip</i> it or <i>finish</i>?"
            )

        def ask_for_task_state():
            return (
                "Say <i>complete</i> to complete the current task.<br>"
                "Say <i>switch</i> to switch to a different task."
            )

        def pomodoro_trans(message):
            self.chosen_task = None
            msg = ""
            if message is None:
                message = ""
            if find_whole_word("no")(message):
                return "end_state", "I hope you'll have a productive session!"

            if find_whole_word("yes")(message):
                next_state = "break"
                wake_up_reply = "Good Work! You finished your session.<br>"
                wake_up_reply += ask_for_break()
                wake_up_reply = Reply(wake_up_reply)
            else:
                try:
                    set_chosen_task(message)
                except NonUniqueTaskException:
                    return "pomodoro", "This task is not unique. Choose by ID."

                if self.chosen_task:
                    msg += f"Task chosen: {self.chosen_task['content']}.<br>"
                    next_state = "pom_review"
                    wake_up_reply = Reply(
                        "Good Work! You finished your session."
                        "<br>Did you <i>complete</i> your task?"
                    )
                else:
                    msg = (
                        "I did not get that. "
                        "Please answer with yes, no, a task name or a task id."
                    )
                    return "pomodoro", msg

            minutes = self.pref["pomodoro_minutes"]
            delta = timedelta(minutes=minutes)

            if not self.enough_time_for(delta):
                msg = (
                    "Can't start another pomodoro. "
                    "You should get going on your journey. <br>"
                )
                return "end_state", {"message": msg, "table": self.journey.to_table()}

            self.wait_until(
                when=dt.now(pytz.utc) + delta,
                next_state=next_state,
                reply=wake_up_reply,
            )

            msg += f"I will notify you in {minutes} minutes."
            if self.chosen_task:
                msg += "<br>" + ask_for_task_state()

            return "wait_state", msg

        def pom_review_trans(message):
            msg = ""
            if find_whole_word("yes")(message):
                self.todo_service.complete_todo(self.chosen_task)
                msg += "Successfully completed. <br>"
                self.update_todos()

            msg += ask_for_break()
            return "break", msg

        def break_trans(message):
            if message is None:
                message = ""

            if find_whole_word("skip")(message):
                return "pomodoro", get_ask_for_pomodoro_msg()

            if find_whole_word("finish")(message):
                return "end_state", "Okay let's finish up. See you."

            if find_whole_word("break")(message):
                minutes = self.pref["break_minutes"]
                delta = timedelta(minutes=minutes)

                if not self.enough_time_for(delta):
                    msg = (
                        "Can't start another break."
                        "You should get going on your journey. <br>"
                    )
                    return (
                        "end_state",
                        {"message": msg, "table": self.journey.to_table()},
                    )

                msg = "Your break is over. Let's get back to work.<br>"
                msg += get_ask_for_pomodoro_msg()

                self.wait_until(
                    when=dt.now(pytz.utc) + delta,
                    next_state="pomodoro",
                    reply=Reply(msg),
                )
                return "wait_state", f"I will notify you in {minutes} minutes."

            msg = (
                "I did not get that. " "Please answer with (break, skip or finish)."
            )
            return "break", msg

        def cancel_interval():
            if self.wake_job.next_run_time < dt.now(pytz.utc):
                raise Exception("Called cancel in non-waiting state")

            func = self.wake_job.func
            job_args = self.wake_job.args
            job_kwargs = self.wake_job.kwargs

            func(*job_args, **job_kwargs)
            self.wake_job.remove()
            self.wake_job = None

        def choosing_todo_trans(message):
            self.chosen_task = None
            if message.lower() == "none":
                return "wait_state", "No task chosen."
            if message.lower() == "finish":
                cancel_interval()
                return None, ""

            try:
                set_chosen_task(message)
            except NonUniqueTaskException:
                return "choosing_todo", "This task is not unique. Choose by ID."

            if self.chosen_task:
                self.choosing = False
                return "wait_state", f"Switched to {self.chosen_task['content']}."

            msg = "I could not match that to any task."
            return "choosing_todo", msg

        def wait_trans(message):
            if not (self.expire_by and self.wake_job):
                raise Exception("in wait_state even though timer expired")

            msg = ""
            if find_whole_word("cancel")(message):
                cancel_interval()
                return None, ""

            if self.chosen_task and (
                find_whole_word("complete")(message)
                or find_whole_word("switch")(message)
            ):

                if find_whole_word("complete")(message):
                    try:
                        self.todo_service.complete_todo(self.chosen_task)
                        msg += "Successfully completed. "
                        self.update_todos()
                    except Exception as e:
                        print("Could not complete the task: ", e)
                        msg += "Failed to commit the complete. "

                if self.todo_table:
                    msg += "Choose a new task, " "say <i>none</i> or " "<i>finish</i>."
                return "choosing_todo", {"message": msg, "table": self.todo_table}

            period = self.expire_by - dt.now(pytz.utc)
            minutes, seconds = divmod(period.seconds, 60)
            msg = (
                "Timer running. "
                f"I will notify you in {minutes}:{seconds}.<br>"
                "Enter <i>cancel</i> to skip forward."
            )
            if self.chosen_task:
                msg += "<br>" + ask_for_task_state()
            return "wait_state", msg

        m = self.fsm
        m.add_state("start", start_trans)
        m.set_start("start")
        m.add_state("no_journey", no_journey_trans)
        m.add_state("music", music_trans)
        m.add_state("todo", todo_trans)
        m.add_state("pomodoro", pomodoro_trans)
        m.add_state("pom_review", pom_review_trans)
        m.add_state("break", break_trans)
        m.add_state("wait_state", wait_trans)
        m.add_state("choosing_todo", choosing_todo_trans)
        m.add_state("error_state", None, end_state=True)
        m.add_state("end_state", None, end_state=True)

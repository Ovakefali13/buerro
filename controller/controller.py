from http.server import BaseHTTPRequestHandler
import json
from apscheduler.schedulers.base import BaseScheduler

from chatbot import Chatbot
from handler import NotificationHandler, LocationHandler, UsecaseStore
from usecase import Reply

def ControllerFromArgs(scheduler: BaseScheduler, chatbot: Chatbot):
    class CustomController(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.scheduler = scheduler
            UsecaseStore.instance().set_scheduler(scheduler)
            self.chatbot = chatbot

            self.notification_handler = NotificationHandler.instance()
            self.location_handler = LocationHandler.instance()

            super(CustomController, self).__init__(*args, **kwargs)

            self.last_location = None

        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers", "Content-type, Authorization"
            )
            BaseHTTPRequestHandler.end_headers(self)

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

        def do_POST(self):
            def respond_json(http_code: int, body: dict):
                self.send_response(http_code)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(body).encode("utf-8"))

            def respond_succ(message=None):
                answer = {
                    "success": True,
                }
                if isinstance(message, str):
                    answer["data"] = {"message": message}
                elif isinstance(message, dict):
                    answer["data"] = {**message}
                elif message is None:
                    pass
                else:
                    breakpoint()
                    respond_error(500, "Unrecognized return type for success")
                    raise Exception("Unrecognized return type for success")
                respond_json(200, answer)

            def respond_error(http_code, message: str):
                answer = {"error": {"message": message}}
                respond_json(http_code, answer)

            def parse_body():
                length = int(self.headers["Content-Length"])
                payload = self.rfile.read(length).decode("utf-8")
                return json.loads(payload)

            body = parse_body()

            if self.path == "/message":

                if body.get("location") and len(body["location"]) == 2:
                    lat, lon = tuple(body["location"])
                    self.location_handler.set(lat, lon)

                msg = body.get("message", "")

                if msg == "shutdown":
                    respond_succ("shutdown")
                else:
                    reply = None
                    store = UsecaseStore.instance()
                    usecase = store.get_running()
                    if not usecase:
                        UsecaseCls = self.chatbot.get_usecase(msg)

                        if not UsecaseCls:
                            msg = ("I did not understand that. \n"
                                          "Try one of the following: ")

                            example_sentences = [
                                "I want to start working.",
                                "I want to travel from Stuttgart to Frankfurt and arrive at 4 p.m.",
                                "I want to travel home now",
                                "I want to cook today",
                                "Where can I go for lunch?",

                            ]

                            reply = Reply({'message': msg, 'list': example_sentences})
                            respond_succ(reply.to_html())
                            del msg
                            return

                        usecase = store.get(UsecaseCls)

                    reply = usecase.advance(msg)
                    if usecase.is_finished():
                        store.usecase_finished()
                    else:
                        store.set_running(usecase)

                    if not isinstance(reply, Reply):
                        respond_error(500, "usecase advance does not Reply")
                        raise Exception(
                            f"Usecase {usecase}'s advance does"
                            + " not return a Reply object"
                        )

                    respond_succ(reply.to_html())
                del msg

            elif self.path == "/save-subscription":
                print("/save-subscription ...")
                try:
                    self.notification_handler.save_subscription(body)
                    respond_succ()
                except Exception as e:
                    print(e)
                    respond_error(
                        500,
                        "The subscription was received but we were unable to"
                        + "save it to our database.",
                    )

            elif self.path == "/location":
                if "location" in body and len(body["location"]) == 2:
                    lat, lon = tuple(body["location"])
                    self.location_handler.set(lat, lon)
                    respond_succ()

                    del lat, lon
                else:
                    respond_error(400, "bad location request")
            else:
                respond_error(404, "Not Found")

            del body

    return CustomController

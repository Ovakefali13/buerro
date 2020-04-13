from abc import ABC, abstractmethod
import inspect
from usecase import Usecase, \
    Lunchbreak, WorkSession, Cook, Transport

class ChatbotBehavior(ABC):
    @abstractmethod
    def get_usecase(self, prompt):
        pass

    @abstractmethod
    def clear_context(self):
        pass

class BuerroBot(ChatbotBehavior):

    context = None
    usecase_by_keyword = {
        "travel": Transport,
        "work session": WorkSession,
        "working": WorkSession,
        "lunch": Lunchbreak,
        #"github": Github,
        "cook": Cook
    }

    def __init__(self):
        for usecase in self.usecase_by_keyword.values():
            if not issubclass(usecase, Usecase):
                raise Exception(f'Usecase {usecase} is not a sub-class of '
                    +'Usecase')

    def get_usecase(self, prompt):
        if prompt == None or prompt == "":
            return None
        prompt = prompt.lower()
        response = self.parse_dic(self.usecase_by_keyword, prompt)
        if inspect.isclass(response) and issubclass(response, Usecase):
            return response
        else:
            return None

    def parse_dic(self, dic, prompt):
        for key, value in dic.items():
            if key in prompt:
                if inspect.isclass(value) and issubclass(value, Usecase):
                    return value
                elif isinstance(value, dict):
                    return self.parse_dic(value, prompt)
                else:
                    raise Exception(("keyword to usecase dictionary "
                                    f"contains an invalid type: {type(value)}"))

    def clear_context(self):
        context = None

class Chatbot:
    behaviour = None

    def __init__(self, behaviour):
        self.behaviour = behaviour

    def get_usecase(self, prompt):
        return self.behaviour.get_usecase(prompt)

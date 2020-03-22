from abc import ABC, abstractmethod

class ChatbotBehavior(ABC):
    @abstractmethod
    def get_context(self, prompt):
        pass

    @abstractmethod
    def clear_context(self):
        pass

class BuerroBot(ChatbotBehavior):

    context = None
    keyword_dict = {
        "bahn": {
            "uni": "$$next_train_to_university"
        },
        "kalender": "$$next_calendar_event"
    }

    def get_context(self, prompt):
        if prompt == None or prompt == "":
            return "$$undefined_behaviour"
        prompt = prompt.lower()
        response = self.parse_dic(self.keyword_dict, prompt)
        if type(response) is str:
            return response
        else:
            return "$$undefined_behaviour"

    def parse_dic(self, dic, prompt):
        for key in dic.keys():
            if key in prompt:
                if type(dic[key]) is str:
                    return dic[key]
                else:
                    return self.parse_dic(dic[key], prompt)

    def clear_context(self):
        context = None

class Chatbot:
    behaviour = None

    def __init__(self, behaviour):
        self.behaviour = behaviour

    def get_context(self, prompt):
        return self.behaviour.get_context(prompt)

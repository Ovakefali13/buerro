from abc import ABC, abstractmethod

class ChatbotBehaviour(ABC):
    @abstractmethod
    def get_response(self, prompt):
        pass

    @abstractmethod
    def clear_context(self):
        pass

class BuerroBot(ChatbotBehaviour):

    context = None
    keyword_dict = {
        "bahn": {
            "uni": "$$next_train_to_university"
        },
        "kalender": "$$next_calendar_event"
    }

    def get_response(self, prompt):
        if prompt == None or prompt == "":
            return "$$undefined_behaviour"
        prompt = prompt.lower()
        for key in self.keyword_dict.keys():
            if key in prompt:
                if type(self.keyword_dict[key]) is str:
                    return self.keyword_dict[key]
                else:
                    for key_n in self.keyword_dict[key].keys():
                        if key_n in prompt:
                            if type(self.keyword_dict[key][key_n]) is str:
                                return self.keyword_dict[key][key_n]
        return "$$undefined_behaviour"
    
    def clear_context(self):
        context = None

class Chatbot:
    behaviour = None

    def __init__(self, behaviour):
        self.behaviour = behaviour

    def get_response(self, prompt):
        return self.behaviour.get_response(prompt)
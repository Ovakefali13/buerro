from abc import ABC, abstractmethod
from util import MetaSingleton

class Chatbot(ABC):

    @abstractmethod
    def get_intent(self, message:str):
        pass

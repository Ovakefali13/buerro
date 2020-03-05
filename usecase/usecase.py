from abc import ABC, abstractmethod
from util import MetaSingleton

class Usecase(ABC):
    @abstractmethod
    def advance(self):
        pass

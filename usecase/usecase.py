from abc import ABC, abstractmethod

class Usecase(ABC):
    @abstractmethod
    def advance(self):
        pass

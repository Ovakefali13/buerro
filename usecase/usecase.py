from abc import ABC, abstractmethod

class Usecase(ABC):
    @abstractmethod
    def advance(self):
        pass


class CaselessDict(dict):
    """ A dictionary sub-class with case-insensitive keys """

    def __setitem__(self, key, value):
        if isinstance(key, str):
            key = key.casefold()
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if isinstance(key, str):
            key = key.casefold()
        return super().__getitem__(key)

class Reply(CaselessDict):
    attributes = ('message', 'link', 'list', 'dict')

    def __init__(self, values:dict):
        for key in values:
            if key not in self.attributes:
                raise Exception('Provided an undefined reply attribute, '
                    + 'only allowed attributes: ' + self.attributes)
            self[key] = values[key]

    def __setitem__(self, key, value):
        if key not in self.attributes:
            raise Exception('Provided an undefined reply attribute, '
                + 'only allowed attributes: ' + self.attributes)
        setattr(self, key, value)
        super().__setitem__(key, value)

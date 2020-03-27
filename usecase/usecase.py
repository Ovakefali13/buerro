from abc import ABC, abstractmethod
from dominate import tags


class FinishedException(Exception):
    pass

class Usecase(ABC):

    @abstractmethod
    def advance(self, message:str):
        pass

    @abstractmethod
    def is_finished(self):
        pass

    @abstractmethod
    def set_default_services(self):
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

from handler import Notification

class Reply(CaselessDict):
    attributes = ('message', 'link', 'list', 'dict', 'table')

    def __init__(self, values):

        if isinstance(values, str):
            self['message'] = values

        elif isinstance(values, dict):
            for key in values:
                if key not in self.attributes:
                    raise Exception('Provided an undefined reply attribute, '
                        + 'only allowed attributes: ' + self.attributes)
                self[key] = values[key]
        elif values is None:
            pass
        else:
            raise Exception("""Provided values of improper type {wrong_type}: either
                                Reply("I created an event.")
                                # or
                                Reply({{
                                    'message': 'How about this restaurant?',
                                    'link': restaurant_link
                                }})""".format(wrong_type=type(values)))

    def __setitem__(self, key, value):
        if key not in self.attributes:
            raise Exception('Provided an undefined reply attribute, '
                + 'only allowed attributes: ' + self.attributes)
        setattr(self, key, value)
        super().__setitem__(key, value)

    def to_html(self):
        html = ""
        for key in self.attributes:
            if key in self:
                value = self[key]
                if key == 'message':
                    html += value

                if key == 'link':
                    html += '\n<br>\n'+ str(tags.a(value, href=value))

                if key == 'list':
                    if not isinstance(value, list):
                        raise Exception("Passed non-list as a list to reply")
                    l = tags.ul()
                    for el in value:
                        l += tags.li(el)
                    html += '\n<br>\n'+ str(l)

                if key == 'dict':
                    if not isinstance(value, dict):
                        raise Exception("Passed non-dict as dict to reply")

                    with tags.table() as table:
                        with tags.tbody() as tbody:
                            for k, v in value.items():
                                with tags.tr() as row:
                                    tags.td(k)
                                    tags.td(v)

                    html += '\n<br>\n'+ str(table)

                if key == 'table':
                    if not isinstance(value, dict):
                        raise Exception("Passed non-dict as dict to reply")
                    if not all(len(listA) == len(listB)
                        for listA in value.values() for listB in value.values()):
                        raise Exception("Provided lists do not have the same length")

                    columns = value.keys()
                    with tags.table() as table:
                        with tags.thead() as head:
                            for col in columns:
                                tags.th(col)
                        with tags.tbody() as body:
                            tuples = zip(*value.values())
                            for row in tuples:
                                with tags.tr() as html_row:
                                    for val in row:
                                        tags.td(val)

                    html += '\n<br>\n' + str(table)
        return html

    def to_notification(self):
        if not self.message:
            raise Exception("At least set a message.")

        notification = Notification(self.message)
        notification.add_message(self.message)
        return notification

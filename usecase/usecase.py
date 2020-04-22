from abc import ABC, abstractmethod
from util import link_to_html, list_to_html, dict_to_html, table_to_html


class FinishedException(Exception):
    pass


class Usecase(ABC):
    @abstractmethod
    def advance(self, message: str):
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
    attributes = ("message", "link", "list", "dict", "table")

    def __init__(self, values):

        if isinstance(values, str):
            self["message"] = values

        elif isinstance(values, dict):
            for key in values:
                if key not in self.attributes:
                    raise Exception(
                        "Provided an undefined reply attribute, "
                        + "only allowed attributes: "
                        + self.attributes
                    )
                self[key] = values[key]
        elif values is None:
            pass
        else:
            raise Exception(
                """Provided values of improper type {wrong_type}: either
                                Reply("I created an event.")
                                # or
                                Reply({{
                                    'message': 'How about this restaurant?',
                                    'link': restaurant_link
                                }})""".format(
                    wrong_type=type(values)
                )
            )

    def __setitem__(self, key, value):
        if key not in self.attributes:
            raise Exception(
                "Provided an undefined reply attribute, "
                + "only allowed attributes: "
                + self.attributes
            )
        setattr(self, key, value)
        super().__setitem__(key, value)

    def to_html(self):
        html = ""
        for key in self.attributes:
            if key in self:
                value = self[key]
                if key == "message":
                    html += value

                if key == "link":
                    html += "\n<br>\n" + link_to_html(value)

                if key == "list":
                    html += "\n<br>\n" + list_to_html(value)

                if key == "dict":
                    html += "\n<br>\n" + dict_to_html(value)

                if key == "table":
                    html += "\n<br>\n" + table_to_html(value)

        return html

    def to_notification(self):
        if not self.message:
            raise Exception("At least set a message.")

        notification = Notification(self.message)
        notification.add_message(self.message)
        return notification

import unittest
from unittest.mock import patch
import asyncio

from main import Main
from usecase import Usecase
from handler import UsecaseStore


class MockUsecase(Usecase):
    def __init__(self):
        self.count = 0

    def advance(self, message):
        if self.is_finished():
            self.reset()
        self.count += 1
        if self.count == 1:
            return "test1"
        if self.count == 2:
            return "test2"
        raise Exception("advanced finished usecase")

    def is_finished(self):
        return self.count == 2

    def reset(self):
        self.count = 0

    def set_default_services(self):
        pass


class QuicklyFinishedUsecase(Usecase):
    def __init__(self):
        self.count = 0

    def set_event(self, event):
        self.event = event

    def advance(self, message):
        if self.is_finished():
            self.reset()
        self.count += 1
        if self.count == 1:
            return Reply(
                "This usecase is already over. Hopy you enjoyed \
                        the show"
            )

    def reset(self):
        self.count = 0

    def is_finished(self):
        return self.count == 1

    def set_default_services(self):
        pass

    def proactive_func(self, arg, kwarg):
        self.event.set()


class TestMain(unittest.TestCase):
    @patch.object(Main, "schedule_usecases")
    def test_block_trigger(self, mock_schedule):
        event = asyncio.Event()

        main = Main()
        mock_schedule.assert_called()
        # schedule trigger...

        store = UsecaseStore.instance()
        store.purge()
        usecase = store.get(MockUsecase)

        usecase.advance("foo")
        self.assertFalse(usecase.is_finished())
        store.set_running(usecase)

        proactive_usecase = store.get(QuicklyFinishedUsecase)
        proactive_usecase.set_event(event)

        # Scheduled trigger returns -> block_trigger
        main.block_trigger(
            proactive_usecase, proactive_usecase.proactive_func, 123, kwarg="abc"
        )

        self.assertFalse(event.is_set())

        usecase.advance("bar")
        self.assertTrue(usecase.is_finished())
        store.usecase_finished()

        self.assertTrue(event.is_set())

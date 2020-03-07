import unittest
from .. import Lunchbreak

class TestLunchbreak(unittest.TestCase):
    MOCK_LOCATION = 'Stuttgart'

    def test_checkLunchOptions(self):
        lb = Lunchbreak(self.MOCK_LOCATION, True)
        # TODO optional agruments

    def tets_check_lunch_options(self):
        lb = Lunchbreak(self.MOCK_LOCATION, True)
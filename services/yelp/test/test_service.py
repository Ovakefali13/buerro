import unittest
import os
import json
from datetime import datetime

from services.yelp import YelpService, YelpServiceRemote, YelpServiceModule, YelpRequest
from util import Singleton


@Singleton
class YelpMock(YelpServiceModule):
    def request_businesses(self, search_param):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "mock_yelp_restaurants.json")
        with open(filename, "r") as mockRestaurant_f:
            mockRestaurant = json.load(mockRestaurant_f)
        return mockRestaurant

    def request_business(self, id):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "mock_yelp_restaurants_focused.json")
        with open(filename, "r") as mockFRestaurant_f:
            mockFocusedRestaurant = json.load(mockFRestaurant_f)
        return mockFocusedRestaurant


class TestYelpService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if "DONOTMOCK" in os.environ:
            self.yelp_service = YelpService.instance(
                remote=YelpServiceRemote.instance()
            )
        else:
            print("Mocking remotes...")
            self.yelp_service = YelpService.instance(remote=YelpMock.instance())

        self.search_params = YelpRequest()
        self.search_params.set_location("Jägerstraße 56, 70174 Stuttgart")

        mock_request_time = datetime.timestamp(
            datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        )
        self.search_params.set_time(mock_request_time)

        self.search_params.set_radius(120, True)

    def test_get_short_information_of_restaurants(self):
        short_information = self.yelp_service.get_short_information_of_restaurants(
            self.search_params
        )
        self.assertIsInstance(short_information[0]["name"], str)

    def test_get_short_information_of_restaurant(self):
        short_information = self.yelp_service.get_short_information_of_restaurants(
            self.search_params
        )
        short_info_focused = self.yelp_service.get_business(short_information[0]["id"])
        self.assertIsInstance(short_info_focused["name"], str)

    def test_get_businesses(self):
        information = self.yelp_service.get_businesses(self.search_params)
        self.assertIsInstance(information["businesses"][0]["name"], str)

    def test_get_next_business(self):
        next_restaurant = self.yelp_service.get_next_business(self.search_params)
        self.assertIsInstance(next_restaurant["name"], str)

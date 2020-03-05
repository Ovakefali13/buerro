import unittest
import os
import json


from .. import YelpService,YelpServiceRemote, YelpServiceModule


class YelpMock(YelpServiceModule):

    def requestBusinesses(self):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_yelp_restaurants.json'), 'r') as mockRestaurant_f:
            mockRestaurant = json.load(mockRestaurant_f)
        return mockRestaurant


    def requestBusiness(self, id):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_yelp_restaurants_focused.json'), 'r') as mockFRestaurant_f:
            mockFocusedRestaurant = json.load(mockFRestaurant_f)
        return mockFocusedRestaurant


class TestYelpService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = YelpServiceRemote()
    else:
        print("Mocking remotes...")
        remote = YelpMock()


    yelpService = None


    def test_getShortInformationOfRestaurants(self):
        self.yelpService = YelpService.instance()
        self.yelpService.setRemote(self.remote)
        self.yelpService.setRadius(60, True)
        self.yelpService.requestBusinesses(1583160868, 'Stuttgart')
        shortInformation = self.yelpService.getShortInformationOfRestaurants()
        self.assertEquals(shortInformation[0]['name'], 'Gasthaus Bären')



    def test_getShortInformationOfRestaurant(self):
        self.yelpService = YelpService.instance()
        self.yelpService.setRemote(self.remote)
        self.yelpService.setRadius(60, False)
        self.yelpService.requestBusinesses(1583160868, 'Stuttgart')
        shortInformation = self.yelpService.getShortInformationOfRestaurants()
        self.yelpService.requestBusiness(shortInformation[0]['id'])
        shortInfoFocused = self.yelpService.getBusinessInformation()

        self.assertEquals(shortInfoFocused['name'], 'Gasthaus Bären')


    def test_getDelivery(self):
        self.yelpService = YelpService.instance()
        self.yelpService.setRemote(self.remote)
        self.yelpService.setRadius(60, False)
        self.yelpService.setLimit(60)
        self.yelpService.requestBusinesses(1583160868, 'Stuttgart')

        nextDelivery = self.yelpService.getDelivery()

        self.assertEquals(nextDelivery, )
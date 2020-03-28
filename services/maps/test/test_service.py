import unittest
import os
import json
from util import Singleton
from .. import MapService, MapRemote, MapJSONRemote, GeocodingService, GeocodingRemote, GeocodingJSONRemote

@Singleton
class MapMockRemote():

    def get_route_information(self, start:list, dest:list, travel_mode:str):
        if travel_mode != 'driving-car':
            return

        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_route.json'), 'r') as f:
            mock_route = json.load(f)

        return mock_route


class TestMapService(unittest.TestCase):

    if 'DONOTMOCK' in os.environ:
        map_service = MapService.instance(MapJSONRemote.instance())
    else:
        map_service = MapService.instance(MapMockRemote.instance())


    dhbw = [48.773563, 9.170963]
    mensa = [48.780834, 9.169989]


    def test_get_summary(self):
        summary = self.map_service.get_route_summary(self.dhbw, self.mensa, 'driving-car')
        self.assertEqual(summary, {'start': self.dhbw, 'dest': self.mensa, 'distance': 1295.7, 'duration': 238.0})


    def test_get_route_link(self):
        link = self.map_service.get_route_link(self.dhbw, self.mensa)
        self.assertEqual(link, 'https://routing.openstreetmap.de/?loc=48.773563%2C9.170963&loc=48.780834%2C9.169989&hl=en&srv=1')

@Singleton
class GeocodingMockRemote():
    # dhbw = ['Rotebühlplatz 41, 70178 Stuttgart, Deutschland', [48.7735115, 9.1710448]]

    def get_information_from_address(self, address:str):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_from_address.json'), 'r') as f:
            mock_from_address = json.load(f)
        return mock_from_address


    def get_information_from_coords(self, coords:list):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'mock_from_coords.json'), 'r') as f:
            mock_from_coords = json.load(f)
        return mock_from_coords


class TestGeocodingService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        geocoding_service = GeocodingService.instance(
            GeocodingJSONRemote.instance())
    else:
        geocoding_service = GeocodingService.instance(
            GeocodingMockRemote.instance())

    dhbw = ['Rotebühlplatz 41 70178 Stuttgart', [48.7735115, 9.1710448]]

    def test_get_coords_from_adress(self):
        coords = self.geocoding_service.get_coords_from_address(self.dhbw[0])
        self.assertEqual(coords, self.dhbw[1])


    def test_get_address_from_coords(self):
        address = self.geocoding_service.get_address_from_coords(self.dhbw[1])
        self.assertEqual(address, self.dhbw[0])


    def test_get_city_from_coords(self):
        city = self.geocoding_service.get_city_from_coords(self.dhbw[1])
        self.assertEqual(city, 'Stuttgart')

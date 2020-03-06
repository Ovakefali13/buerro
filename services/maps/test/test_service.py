import unittest
import os
import json
from .. import MapService, MapRemote, MapJSONRemote, GeocodingService, GeocodingRemote, GeocodingJSONRemote


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
        remote = MapJSONRemote()
    else:
        print("Mocking remotes...")
        remote = MapMockRemote()

    map_service = MapService(remote)

    dhbw = [48.773563, 9.170963]
    mensa = [48.780834, 9.169989]


    def test_get_summary(self):
        summary = self.map_service.get_route_summary(self.dhbw, self.mensa, 'driving-car')
        self.assertEqual(summary, {'start': self.dhbw, 'dest': self.mensa, 'distance': 1295.7, 'duration': 238.0})


    def test_get_route_link(self):
        link = self.map_service.get_route_link(self.dhbw, self.mensa)
        self.assertEqual(link, 'https://routing.openstreetmap.de/?loc=48.773563%2C9.170963&loc=48.780834%2C9.169989&hl=de')


class GeocodingMockRemote():    
    dhbw = ['Rotebühlplatz 41, 70178 Stuttgart, Deutschland', [48.7735115, 9.1710448]]


    def get_information_from_address(self, address:str):
        if address == self.dhbw[0]:
            dirname = os.path.dirname(__file__)
            with open(os.path.join(dirname, 'mock_from_address.json'), 'r') as f:
                mock_from_address = json.load(f)
            return mock_from_address

    
    def get_information_from_coords(self, coords:list):
        if coords == self.dhbw[1]:
            dirname = os.path.dirname(__file__)            
            with open(os.path.join(dirname, 'mock_from_coords.json'), 'r') as f:
                mock_from_coords = json.load(f)
            return mock_from_coords


class TestGeocodingService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = GeocodingJSONRemote()
    else:
        print("Mocking remotes...")
        remote = GeocodingMockRemote()

    geocoding_service = GeocodingService(remote)
    dhbw = ['Rotebühlplatz 41, 70178 Stuttgart, Deutschland', [48.7735115, 9.1710448]]

    def test_get_coords_from_adress(self):
        coords = self.geocoding_service.get_coords_from_address(self.dhbw[0])
        self.assertEqual(coords, self.dhbw[1])


    def test_get_address_from_coords(self):
        address = self.geocoding_service.get_address_from_cords(self.dhbw[1])
        self.assertEqual(address, self.dhbw[0])    

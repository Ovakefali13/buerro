import unittest
from .. import routing, geocoding


class MapMockRemote():    

    def get_route_summary(self, start, dest, travel_mode):
        if travel_mode not 'driving-car':
            return ()
        dhbw = ['Rotebühlplatz 41-1, 70178, Stuttgart', [9.170963, 48.773563]]
        mensa = ['Holzgartenstraße 11, 70174 Stuttgart', [9.169989, 48.780834]]
        if start == dhbw[0] and dest == mensa[0]:
            return (1274.7, 238.5)
        elif start == dhbw[1] and dest == mensa[1]:
            return (1295.7, 238.0)
        return ()


class TestMapService(unittest.TestCase):
    map_service = MapMockRemote()

    def test_get_summary(self):
        dhbw = ['Rotebühlplatz 41-1, 70178, Stuttgart', [9.170963, 48.773563]]
        mensa = ['Holzgartenstraße 11, 70174 Stuttgart', [9.169989, 48.780834]]

        summary = self.map_service.get_route_summary(dhbw[0], mensa[0], 'driving-car')
        self.assertEqual(summary, (1274.7, 238.5))

        summary = self.map_service.get_route_summary(dhbw[1], mensa[1], 'driving-car')
        self.assertEqual(summary, (1295.7, 238.0))

import unittest
import datetime

from usecase.usecase import Reply
from usecase.transport import Transport
from services.weatherAPI import WeatherAdapter
from services.preferences import PrefService, PrefJSONRemote
from services.maps import GeocodingService, MapService
from services.vvs import VVSService, VVSEfaJSONRemote
from services.weatherAPI.test import WeatherMock
from services.maps.test import MapMockRemote, GeocodingMockRemote
from services.vss.test import VVSMockRemote

class TestTransport(unittest.TestCase):
    dhbw = [48.773563, 9.170963]
    mensa = [48.780834, 9.169989]
            
    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.pref_service=PrefService(PrefJSONRemote()),
            self.map_service=MapService.instance(),
            self.vvs_service=VVSService.instance(VVSEfaJSONRemote.instance()),
            self.geo_service=GeocodingService.instance(),
            self.wea_service=WeatherAdapter.instance()):
        else:
            print("Mocking remotes...")
            self.pref_service=PrefService(PrefJSONRemote()),
            self.map_service=MapService.instance(),
            self.vvs_service=VVSService.instance(VVSEfaJSONRemote.instance()),
            self.geo_service=GeocodingService.instance(),
            self.wea_service=WeatherAdapter.instance()):

        self.use_case = Transport()
        self.use_case.set_services(
            pref_service=self.pref_service
            map_service=self.map_service
            vvs_service=self.vvs_service
            geo_service=self.geo_service
            wea_service=self.wea_service
        )

    def test_usecase(self):
        reply = self.use_case.advance('I want to go from home to the university and arrive at 10 pm.')
        response_message = self.use_case.get_response()
        self.assertIsInstance(reply, Reply)
        self.assertEquals('pork', self.use_case.ingredient)
        self.assertIs(type(response_message), str)
        


    


    

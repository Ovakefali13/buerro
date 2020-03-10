from services.weatherAPI.weather_service import WeatherAdapter, WeatherAdapterRemote
from services.preferences import PrefService, PrefJSONRemote
from services.maps import GeocodingService, GeocodingJSONRemote, MapService, MapJSONRemote
from services.maps.test.test_service import GeocodingMockRemote, MapMockRemote
from services.vvs import VVSService, VVSEfaJSONRemote
from multiprocessing import Process
import time

class Transport: 
    transport_info = {
        'Start': None,
        'Dest': None,
        'Cycling': None,
        'Car': None,
        'Walking': None,
        'VVS': None,
        'Weather': None
    }
    
    def __init__(self):        

        self.trigger_use_case([],[],0)
    
            
    def trigger_use_case(self, start:list, dest:list, travel_time:int):
        print('trigger_use_case')
        self.load_preferences()
        self.get_transport_information([],[],0)
    

    def load_preferences(self):
        print('load_preferences')
        self.pref_service = PrefService(PrefJSONRemote())
        self.preferences_json = self.pref_service.get_preferences('transport')   


    def get_transport_information(self, start:list, dest:list, travel_time:int):
        print('get_transport_options')        
        
        def weather_api_call(self):
            weather_adapter = WeatherAdapter.instance()
            

            self.transport_info['Weather'] = 1


        def map_api_call(self):
            map_service = MapService.instance()
            map_service.set_remote(GeocodingMockRemote.instance())
            self.transport_info['Car'] = 2


        def geocoding_api_call(self):
            geocoding_service = GeocodingService.instance()
            geocoding_service.set_remote(GeocodingMockRemote.instance())
            self.transport_info['Cycling'] = 3
            

        def runInParallel(*fns):
            proc = []
            for fn in fns:
                p = Process(target=fn)
                p.start()
                proc.append(p)
            for p in proc:
                p.join()            

        runInParallel(map_api_call(self), geocoding_api_call(self), weather_api_call(self))
        

    def compare_transport_options(self):
        pass

Transport()
from services.weatherAPI.weather_service import WeatherAdapter
from services.preferences import PrefService, PrefJSONRemote
from services.maps import GeocodingService, MapService
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
        self.get_transport_information([48.773563, 9.170963],[48.780834, 9.169989],20)
    

    def load_preferences(self):
        print('load_preferences')
        self.pref_service = PrefService(PrefJSONRemote())
        self.preferences_json = self.pref_service.get_preferences('transport')   


    def get_transport_information(self, start:list, dest:list, travel_time:int):
        print('get_transport_options')        

        geo = GeocodingService.instance()
        
        def weather_service(self):
            wea = WeatherAdapter.instance()
            wea.update(geo.get_city_from_coords(start))
            
            self.transport_info['Weather'] = wea.is_bad_weather()


        def map_service(self):
            maps = MapService.instance()

            args = {
                'Car': 'driving-car',
                'Cycling': 'cycling',
                'Walking': 'foot-walking'
            }

            for name, mode in tuple(args):
                self.transport_info[name] = maps.get_route_summary(start, dest, mode)


        def vvs_service(self):
            vvs = VVSService(VVSEfaJSONRemote())
            #vvs.get_journeys()
            self.transport_info['VVS'] = 3
            

        def runInParallel(*fns):
            proc = []
            for fn in fns:
                p = Process(target=fn)
                p.start()
                proc.append(p)
            for p in proc:
                p.join()            

        runInParallel(weather_service(self), map_service(self), vvs_service(self))
        

    def compare_transport_options(self):
        pass

Transport()
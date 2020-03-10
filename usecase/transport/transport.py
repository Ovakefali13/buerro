from services.weatherAPI.weather_service import WeatherAdapter
from services.preferences import PrefService, PrefJSONRemote
from services.maps import GeocodingService, MapService
from services.vvs import VVSService, VVSEfaJSONRemote
from multiprocessing import Process
from datetime import datetime

class Transport: 
    transport_info = {
        'Start': None,
        'Dest': None,
        'Cycling': None,
        'Car': None,
        'Walking': None,
        'VVS': None,
        'WeatherGood': None,
        'ArrDep': None,
        'Time': None
    }
    
    def __init__(self):
        self.trigger_use_case([48.773563, 9.170963],[48.780834, 9.169989],'dep')
    
            
    def trigger_use_case(self, start:list, dest:list, arr_dep:str, time:datetime=datetime.now()):
        print('trigger_use_case')

        self.transport_info['Start'] = start
        self.transport_info['Dest'] = dest
        self.transport_info['ArrDep'] = arr_dep
        self.transport_info['Time'] = time

        self.load_preferences()
        self.get_transport_information()
    

    def load_preferences(self):
        print('load_preferences')
        self.pref_service = PrefService(PrefJSONRemote())
        self.preferences_json = self.pref_service.get_preferences('transport')   


    def get_transport_information(self):
        print('get_transport_options')        
        geo = GeocodingService.instance()    

        
        def weather_service(self):
            wea = WeatherAdapter.instance()            
            wea.update(geo.get_city_from_coords(self.transport_info['Start']))
            
            self.transport_info['WeatherGood'] = wea.is_bad_weather()


        def map_service(self):
            args = {
                'Car': 'driving-car',
                'Cycling': 'cycling-regular',
                'Walking': 'foot-walking'
            }

            maps = MapService.instance()            

            for name, mode in args.items():
                print(name, mode)

                self.transport_info[name] = maps.get_route_summary(self.transport_info['Start'], self.transport_info['Dest'], mode)


        def vvs_service(self):
            vvs = VVSService(VVSEfaJSONRemote())
            start = geo.get_address_from_coords(self.transport_info['Start'])
            dest = geo.get_address_from_coords(self.transport_info['Dest'])
            arr_dep = self.transport_info['ArrDep']
            time = self.transport_info['Time']
            
            self.transport_info['VVS'] = vvs.get_journeys(start, dest, arr_dep, time)
            

        def runInParallel(*fns):
            proc = []
            for fn in fns:
                p = Process(target=fn)
                p.start()
                proc.append(p)
            for p in proc:
                p.join()            

        runInParallel(weather_service(self), map_service(self), vvs_service(self))
        print(self.transport_info)
        

    def compare_transport_options(self):
        pass

Transport()
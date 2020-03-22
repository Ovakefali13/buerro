from services.weatherAPI.weather_service import WeatherAdapter
from services.preferences import PrefService, PrefJSONRemote
from services.maps import GeocodingService, MapService
from services.vvs import VVSService, VVSEfaJSONRemote
from usecase import Usecase, Reply
from handler import LocationHandler

from multiprocessing import Process
from datetime import datetime, timedelta
import re


class Transport(Usecase): 
    req_info = {
        'Start': None,
        'Dest': None,
        'ArrDep': None,
        'Time': None
    }
    transport_info = {        
        'Cycling': None,
        'Car': None,
        'Walking': None,
        'VVS': None,
        'WeatherGood': None,
    }
    
    def __init__(self):
        self.set_services()
        self.advance('I want to go from the mainstation to home')


    def set_services(self,
                    pref_service:PrefService=PrefService(PrefJSONRemote()),
                    map_service:MapService=MapService.instance(),
                    vvs_service:VVSService=VVSService.instance(VVSEfaJSONRemote.instance()),
                    geo_service:GeocodingService=GeocodingService.instance(),
                    wea_service:WeatherAdapter=WeatherAdapter.instance()):
        self.pref_service = pref_service
        self.pref = pref_service.get_preferences('transport')
        self.map_service = map_service
        self.vvs_service = vvs_service
        self.geo_service = geo_service
        self.wea_service = wea_service


    def advance(self, message):
        if not self.wea_service:
            raise Exception("Set Services!")

        if None in self.req_info.values():
            self.set_transport_parameters(message)

        if None in self.transport_info.values():
            self.get_transport_information()

        
    def is_finished(self):
        return self.is_finished()     

    def set_transport_parameters(self, message):
        special_locations = ['home', 'work', 'mainstation', 'university']

        def get_special_location(location:str):
            return self.pref.get(location + '_coords')

        def get_datetime(time:str):
            strings = time.split()
            hours = int(strings[0])
            now = datetime.now()
            date = None
            
            if 'hours' in strings:
                date = now + timedelta(hours=hours)
            elif 'p.m.' in strings:
                date = now.replace(hour=hours+12,minute=0,second=0)     

            return date        

        def get_location():
            lh = LocationHandler.instance()
            return lh.get()

        """ Regex tested with
        I want to go from Stuttgart to Frankfurt and arrive at 4 p.m.
        Now I want to go to Frankfurt
        I want to go from home to the university and arrive at 10 p.m.
        I want to go home in 2 hours
        I want to go home now
        I want to go home at 6 p.m. 
        I want to go to Stuttgart and depart at 7 a.m.
        I want to go from the mainstation to home
        """

        if not self.req_info['Start']:      
            regex = r'((?<=from\sthe\s)|(?<=from\s(?!the)))(\w*|home)'
            start = re.search(regex, message)
            if start:
                start = start[0]

            if start:
                if start in special_locations:
                    self.req_info['Start'] = get_special_location(start)
                else:
                    self.req_info['Start'] = self.geo_service.get_coords_from_address(start)
            else:
                self.req_info['Start'] = get_location()

        if not self.req_info['Dest']:
            p = re.compile(r'((?<=to\sthe\s)|(?<=to\s(?!(the|go|arrive))))(\w*|home)|(?<=go\s)home')
            dest = p.search(message)
            if dest:
                dest = dest[0]

            if dest:
                if dest in special_locations:
                    self.req_info['Dest'] = get_special_location(dest)
                else:
                    self.req_info['Dest'] = self.geo_service.get_coords_from_address(dest)
        
        if not self.req_info['ArrDep']:
            p = re.compile(r'arrive(d)? at')
            arr_dep = p.search(message)
            if arr_dep:
                arr_dep = arr_dep[0]

            if arr_dep:
                self.req_info['ArrDep'] = 'Arr'
            else:
                self.req_info['ArrDep'] = 'Dep'
            
        if not self.req_info['Time']:
            p = re.compile(r'(?<=at\s)\d{1,2}\s(a.m.|p.m.)|\d{1,2}\shours')
            time = p.search(message)
            if time:
                time = time[0]

            if time:
                self.req_info['Time'] = get_datetime(time)
            else:
                self.req_info['Time'] = datetime.now()



    def get_transport_information(self):
        start_coords = self.req_info.get('Start')
        dest_coords = self.req_info.get('Dest')
        
        def weather_service(self):   
            self.wea_service.update(self.geo_service.get_city_from_coords(start_coords))            
            self.transport_info['WeatherGood'] = self.wea_service.is_bad_weather()


        def map_service(self):
            args = {
                'Car': 'driving-car',
                'Cycling': 'cycling-regular',
                'Walking': 'foot-walking'
            }
            for name, mode in args.items():
                self.transport_info[name] = self.map_service.get_route_summary(start_coords, dest_coords, mode)


        def vvs_service(self):
            start = self.geo_service.get_address_from_coords(start_coords)
            dest = self.geo_service.get_address_from_coords(dest_coords)
            arr_dep = self.req_info.get('ArrDep')
            time = self.req_info.get('Time')
            print(start, dest, arr_dep, time)
            self.transport_info['VVS'] = self.vvs_service.get_journeys(start, dest, arr_dep, time)
            

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
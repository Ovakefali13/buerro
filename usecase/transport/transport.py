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
        self.set_services()
        self.advance('I want to go from home to the university and arrive at 10 pm.')


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

        if not self.transport_info['Start']:
            self.set_transport_parameters(message)

        if not self.transport_info['Cycling']:
            self.get_transport_information()

        
    def is_finished(self):
        return self.is_finished()     

    def set_transport_parameters(self, message):
        special_locations = ['home', 'work', 'mainstation', 'university']

        def get_special_location(location:str):
            return self.pref[location + '_coords']

        def get_datetime(time:str):
            strings = time.split()
            hours = int(strings[0])
            now = datetime.now()
            date = None
            
            if 'hours' in strings:
                date = now + timedelta(hours=hours)
            elif 'pm' in strings:
                date = now.replace(hour=hours+12,minute=0,second=0)     

            return date        

        def get_location():
            lh = LocationHandler.instance()
            return lh.get()

        """ Regex tested with
        I want to go from Stuttgart to Abstatt and arrive at 4 pm.
        Now I want to go to Abstatt.
        I want to go from home to the university and arrive at 10 pm.
        I want to go home in 2 hours.
        I want to go home now.
        I want to go home at 6 pm. 
        I want to go to Stuttgart and depart at 7 am.
        I want to go from the mainstation to home.
        """

        if not self.transport_info['Start']:      
            regex = r'((?<=from\sthe\s)|(?<=from\s(?!the)))(\w*|home)'
            start = re.search(regex, message)[0]

            if start:
                if start in special_locations:
                    self.transport_info['Start'] = get_special_location(start)
                else:
                    self.transport_info['Start'] = self.geo_service.get_coords_from_address(start)
            else:
                self.transport_info['Start'] = get_location()

        if not self.transport_info['Dest']:
            p = re.compile(r'((?<=to\sthe\s)|(?<=to\s(?!(the|go|arrive))))(\w*|home)|(?<=go\s)home')
            dest = p.search(message)[0]
            if dest:
                if dest in special_locations:
                    self.transport_info['Dest'] = get_special_location(dest)
                else:
                    self.transport_info['Dest'] = self.geo_service.get_coords_from_address(dest)
        
        if not self.transport_info['ArrDep']:
            if 'arrive at' in message:
                self.transport_info['ArrDep'] = 'Arr'
            else:
                self.transport_info['ArrDep'] = 'Dep'
            
        if not self.transport_info['Time']:
            p = re.compile(r'(?<=at\s)\d{1,2}\s(am|pm)|\d{1,2}\shours')
            time = p.search(message)[0]
            if time:
                self.transport_info['Time'] = get_datetime(time)
            else:
                self.transport_info['Time'] = datetime.now()



    def get_transport_information(self):
        print('get_transport_information')
        
        def weather_service(self):   
            self.wea_service.update(self.geo_service.get_city_from_coords(self.transport_info['Start']))            
            self.transport_info['WeatherGood'] = self.wea_service.is_bad_weather()


        def map_service(self):
            args = {
                'Car': 'driving-car',
                'Cycling': 'cycling-regular',
                'Walking': 'foot-walking'
            }
            for name, mode in args.items():
                self.transport_info[name] = self.map_service.get_route_summary(self.transport_info['Start'], self.transport_info['Dest'], mode)


        def vvs_service(self):
            start = self.geo_service.get_address_from_coords(self.transport_info['Start'])
            dest = self.geo_service.get_address_from_coords(self.transport_info['Dest'])
            arr_dep = self.transport_info['ArrDep']
            time = self.transport_info['Time']           
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
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
    transport_recommendation = {
        'Favorite': None,
        'Fastest': None,
        'Viable': ['cycling','car','walking','VVS']
    }
    finished = False
    
    def __init__(self):
        self.set_services()


    def set_services(self,
                    pref_service:PrefService=PrefService(PrefJSONRemote()),
                    map_service:MapService=MapService.instance(),
                    vvs_service:VVSService=VVSService.instance(VVSEfaJSONRemote.instance()),
                    geo_service:GeocodingService=GeocodingService.instance(),
                    wea_service:WeatherAdapter=WeatherAdapter.instance()):
        self.pref_service = pref_service
        self.map_service = map_service
        self.vvs_service = vvs_service
        self.geo_service = geo_service
        self.wea_service = wea_service
        
        self.pref = pref_service.get_preferences('transport')


    def get_transport_mode(self, start:list, dest:list, arr_dep:str='Dep', time:datetime=datetime.now()):
        self.req_info['Start'] = start
        self.req_info['Dest'] = dest
        self.req_info['ArrDep'] = arr_dep
        self.req_info['Time'] = time

        return self.advance(None)        


    def advance(self, message):
        if self.finished:
            self.req_info = dict.fromkeys(self.req_info, None)
            self.transport_info = dict.fromkeys(self.transport_info, None)
            self.transport_recommendation = dict.fromkeys(self.transport_recommendation, None)
            self.transport_recommendation['Viable'] = ['cycling','car','walking','VVS']
            self.finished = False

        if not self.wea_service:
            raise Exception("Set Services!")

        if None in self.req_info.values():
            self.set_transport_parameters(message)           

        if None in self.transport_info.values():
            self.get_transport_information()

        options = self.compare_transport_options()
        self.finished = True
        return options

        
    def is_finished(self):
        return self.finished 

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
            elif 'a.m.' in strings:
                date = now.replace(hour=hours,minute=0,second=0)

            if date < now:
                date = date + timedelta(days=1)

            return date        

        def get_location():
            lh = LocationHandler.instance()     
            location = lh.get()       
            return [location[1], location[0]]

        """ Regex tested with
        I want to go from Stuttgart to Frankfurt and arrive at 4 p.m.
        Now I want to go to Frankfurt
        I want to go from home to the university and arrive at 10 p.m.
        I want to go from the mainstation to home in 2 hours
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
            journeys = self.vvs_service.get_journeys(start, dest, arr_dep, time)
            self.transport_info['VVS'] = sorted(journeys, key=lambda x: x.get_duration())[0]
            

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
        viable = self.transport_recommendation.get('Viable')
        cycling = self.transport_info.get('Cycling')
        walking = self.transport_info.get('Walking')
        vvs = self.transport_info.get('VVS')
        car = self.transport_info.get('Car')
        cycling_duration = cycling.get('duration')
        walking_duration = walking.get('duration')
        car_duration = car.get('duration')
        vvs_duration = vvs.get_duration() * 60 # to seconds

        # Check if mode of travel exist
        if vvs is None:
            viable.remove('VVS')
        if cycling is None:
            viable.remove('cycling')
        if walking is None:
            viable.remove('walking')
        if car is None:
            viable.remove('car')
        if not viable:
            return Reply({'message': f'This route is not available.'})

        # Check if weather is good
        if not self.transport_info.get('WeatherGood'):    
            if 'cycling' in viable:
                viable.remove('cycling')
            if 'walking' in viable:            
                viable.remove('walking') 

        # Check if there is enough time to get to the destination in time and if the distance is not too long
        if self.req_info.get('ArrDep') == 'Arr':
            time_left = (self.req_info.get('Time') - datetime.now()).total_seconds()

            if (cycling_duration > time_left or cycling.get('distance') > 30000) and 'cycling' in viable:
                viable.remove('cycling')
            if (walking_duration > time_left or walking.get('distance') > 5000) and 'walking' in viable:
                viable.remove('walking')
            if car_duration > time_left and 'car' in viable:
                viable.remove('car')
            if vvs_duration > time_left and 'VVS' in viable:
                viable.remove('VVS')

            if not viable:
                # TODO provide alternatives 
                return Reply({'message': f'There is not enough time to get to this destination.'})

        
        # Get prefered modes of travel
        walk_or_bike = self.pref.get('walk_or_bike')
        vvs_or_car = self.pref.get('vvs_or_car')        
        if vvs_or_car in viable:                   
            self.transport_recommendation['Favorite'] = vvs_or_car
        # Set walk or bike first because it is healthy ;)
        if walk_or_bike in viable:            
            self.transport_recommendation['Favorite'] = walk_or_bike    

        # Get fastest mode of travel
        self.transport_recommendation['Fastest'] = sorted({
            'cycling': cycling_duration,
            'walking': walking_duration,
            'car': car_duration,
            'VVS': vvs_duration
        })[0]

        fastest = self.transport_recommendation.get('Fastest')
        favorite = self.transport_recommendation.get('Favorite')

        # Create link for favorite mode of transport        
        if favorite == 'VVS':
            link_fav = vvs.to_link()            
        else:
            link_fav = self.map_service.get_route_link(self.req_info.get('Start'), self.req_info.get('Dest'), favorite)

        reply_dict = {'message': f'For this trip your prefered mode of transport {favorite} is available.', 'link': link_fav}

        # TODO Provide link for alternative
        if favorite != fastest:
            reply_dict['message'] = reply_dict['message'] + f' However, the mode {fastest} is faster.'
            
        return Reply(reply_dict)


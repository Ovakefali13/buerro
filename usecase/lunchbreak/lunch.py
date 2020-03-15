from services.weatherAPI.weather_service import WeatherAdapter
from services.weatherAPI.test.test_service import WeatherMock
from services.yelp.yelp_service import YelpService
from services.yelp.test.test_service import YelpMock
from datetime import datetime
from services.preferences import PrefService
from services.maps.geocoding_service import GeocodingJSONRemote
from services.maps.test.test_service import GeocodingMockRemote
from services.maps import MapService, GeocodingService
from services.yelp.yelp_request import YelpRequest
from services.cal.cal_service import CalService, iCloudCaldavRemote, Event
import pytz
import re

class Lunchbreak:

    def __init__(self, mock:bool=False):
        if mock:
            weather_adapter = WeatherAdapter.instance()
            weather_adapter.set_remote(WeatherMock())
            yelp_service = YelpService.instance()
            yelp_service.set_remote(YelpMock())
            geocoding = GeocodingService.instance()
            geocoding.remote = GeocodingMockRemote.instance()
        else:
            geocoding = GeocodingService.instance()
            geocoding.remote = GeocodingJSONRemote.instance()

    def trigger_use_case(self, location:list):
        self.current_location_coords = location
        restaurants, start, end = self.check_lunch_options(location)
        #TODO send restaurants to controller and get user choice
        choice = self.wait_for_user_request("Four")
        choice = 0
        link = self.open_maps_route(location, restaurants[choice])
        self.create_cal_event(start, end,restaurants[choice], link)


    def check_lunch_options(self, location:list):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        #Search for timeslot between 10 and 15 Oclock
        start = datetime.now(pytz.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        end = datetime.now(pytz.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        duration, lunch_start, lunch_end =  self.find_longest_timeslot_between_hours(start,end)
        #print("Your lunchbreak starts at "  + str(lunch_start) + ". You have " + str(duration) + "minutes until your next event")
        lunch_timestamp = datetime.timestamp(lunch_start)

        hours_until_lunch = self.time_diff_in_hours(lunch_start, datetime.now(pytz.utc))

        geocoding = GeocodingService.instance()
        geocoding.remote = GeocodingJSONRemote.instance()
        city = geocoding.get_city_from_coords(location)

        ### Check Weather ###
        weather_adapter = WeatherAdapter.instance()
        weather_adapter.update(city)
        will_be_bad_weather = weather_adapter.will_be_bad_weather(hours_until_lunch)

        search_params = YelpRequest()
        search_params.set_coordinates(location)
        search_params.set_time(lunch_timestamp)
        search_params.set_radius(duration, will_be_bad_weather)

        yelp_service = YelpService.instance()
        restaurants = yelp_service.get_short_information_of_restaurants(search_params)
        #for x in restaurants:
        #    print(x['name'])
        return restaurants, lunch_start, lunch_end


    def open_maps_route(self, location, restaurant):
        coords_dest = restaurant['coordinates']
        map_service = MapService.instance()
        link = map_service.get_route_link(location, coords_dest)
        return link

    def create_cal_event(self, start, end, restaurant, link):
        lunch = Event()
        lunch.set_title('Lunch at ' + restaurant['name'])
        lunch.set_location(restaurant['address'])
        lunch.add('description', "Route information: " + str(link) + "\nWebsite: " + restaurant['url'])
        lunch.set_start(start)
        lunch.set_end(end)
        cal_service = CalService(iCloudCaldavRemote())
        cal_service.add_event(lunch)
        return lunch

    def wait_for_user_request(self, data):
        ### Wait for user decision ###
        seletedRestaurant = 2
        options = [{"One": 1}, {"Two": 2}, {"Three": 3}, {"Four": 4}, {"Five" : 5}]
        for opts in options:
            match = re.search(str(list(opts.keys())[0]) , data, re.IGNORECASE)
            if(match):
                seletedRestaurant = int(list(opts.values())[0])

        #TODO index at one or zero
        return seletedRestaurant

    def time_diff_in_hours(self, date1, date2):
        time_until_lunch = date1 - date2
        days, seconds = time_until_lunch.days, time_until_lunch.seconds
        hoursu_until_lunch = days * 24 + seconds // 3600
        return hoursu_until_lunch


    def find_longest_timeslot_between_hours(self, search_start, search_end):
        cal_service = CalService(iCloudCaldavRemote())
        time, before, after = cal_service.get_max_available_time_between(search_start, search_end)
        return int((time.total_seconds() / 60)), before, after

    def notify(self):
        start = datetime.now(pytz.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        end = datetime.now(pytz.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        duration, lunch_start, lunch_end = self.find_longest_timeslot_between_hours(start, end)

        lunch_timestamp = datetime.timestamp(lunch_start)

        hours_until_lunch = self.time_diff_in_hours(lunch_start, datetime.now(pytz.utc))
        if(hours_until_lunch < 3):
            return True
        else:
            return False

    def trigger_proactive_usecase(self, location):
        if(self.notify()):
            self.trigger_use_case(location)
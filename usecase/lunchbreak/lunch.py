from services.weatherAPI.weather_service import WeatherAdapter
from services.weatherAPI.test.test_service import WeatherMock
from services.yelp.yelp_service import YelpService
from services.yelp.test.test_service import YelpMock
from datetime import datetime
from services.preferences import PrefService
from services.maps.geocoding_service import GeocodingService
from services.maps.map_service import MapService
from services.yelp.yelp_request import YelpRequest
from services.cal.cal_service import CalService, iCloudCaldavRemote
import pytz

class Lunchbreak:

    def __init__(self, mock:bool=False):
        if mock:
            weather_adapter = WeatherAdapter.instance()
            weather_adapter.set_remote(WeatherMock())
            yelp_service = YelpService.instance()
            yelp_service.set_remote(YelpMock())
        #self.triggerUseCase(location)

    def trigger_use_case(self, location):
        self.current_location_coords = location
        restaurants = self.check_lunch_options(location)
        #TODO send restaurants to controller and get user choice
        choice = self.wait_for_user_request()
        chioce = 2
        self.open_maps_route(choice, location, restaurants)


    def check_lunch_options(self, location):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        #Search for timeslot between 10 and 15 Oclock
        start = datetime.now(pytz.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        end = datetime.now(pytz.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        duration, lunch_start, lunch_end =  self.find_longest_timeslot_between_hours(start,end)

        lunch_timestamp = datetime.timestamp(lunch_start)

        hours_until_lunch = self.time_diff_in_hours(lunch_start, datetime.now(pytz.utc))

        geocoding = GeocodingService.instance()
        print(location)
        city = geocoding.get_city_from_coords(location)
        print(city)
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
        for x in restaurants:
            print(x['name'])
        return restaurants


    def open_maps_route(self, choice, location, restaurants):
        coords_dest = restaurants[choice]['coordinates']
        map_service = MapService.instance()
        link = map_service.get_route_link(location, coords_dest)
        print(link)

    def wait_for_user_request(self):
        ### Wait for user decision ###
        seletedRestaurant = 2
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


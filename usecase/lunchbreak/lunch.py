from services.weatherAPI.weather_service import WeatherAdapter
from services.weatherAPI.test.test_service import WeatherMock
from services.yelp.yelp_service import YelpService
from services.yelp.test.test_service import YelpMock
from datetime import datetime
from services.preferences import PrefService
#from services.maps.geocoding_service import GeocodingJSONRemote
#from services.maps.map_service import MapService
from services.yelp.yelp_request import YelpRequest

class Lunchbreak:
    current_location_coords = []

    def __init__(self, mock:bool=False):
        if mock:
            weather_adapter = WeatherAdapter.instance()
            weather_adapter.set_remote(WeatherMock())
            yelp_service = YelpService.instance()
            yelp_service.set_remote(YelpMock())
        #self.triggerUseCase(location)

    def trigger_use_case(self, location):
        self.current_location_coords =[48.76533759999999, 9.161932799999999]
        self.check_lunch_options(location)
        #TODO send restaurants to controller and get user choice
        choice = self.wait_for_user_request()
        self.open_maps_route(choice)


    def check_lunch_options(self, location):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        lunch_start = '2020-03-07T12:00:00'
        duration = 60

        lunch_start_iso = datetime.fromisoformat(lunch_start)
        lunch_timestamp = datetime.timestamp(lunch_start_iso)

        hours_until_lunch = self.time_diff_in_hours(lunch_start_iso, datetime.now())


        #geocoding = GeocodingJSONRemote()
        #print(geocoding.get_information_from_address('Jägerstraße 56, 70174 Stuttgart'))
        #location = geocoding.get_information_from_coords(self.current_location_coords)
        location = 'Jägerstraße 56, 70174 Stuttgart'
        # Todo extract city
        city = 'Stuttgart'

        ### Check Weather ###
        weather_adapter = WeatherAdapter.instance()
        weather_adapter.update(city)
        will_be_bad_weather = weather_adapter.will_be_bad_weather(hours_until_lunch)

        search_params = YelpRequest()
        search_params.set_location(location)
        search_params.set_time(lunch_timestamp)
        search_params.set_radius(duration, will_be_bad_weather)

        yelp_service = YelpService.instance()
        self.restaurants = yelp_service.get_short_information_of_restaurants(search_params)
        for x in self.restaurants:
            print(x['name'])
        return self.restaurants


    def open_maps_route(self, choice):
        coords_dest = self.restaurants[choice]['coordinates']
        #map_service = MapService()
        #link = map_service.get_route_link(self.current_location_coords, coords_dest)
        #print(link)

    def wait_for_user_request(self):
        ### Wait for user decision ###
        seletedRestaurant = 2
        return seletedRestaurant

    def time_diff_in_hours(self, date1, date2):
        time_until_lunch = date1 - date2
        days, seconds = time_until_lunch.days, time_until_lunch.seconds
        hoursu_until_lunch = days * 24 + seconds // 3600
        return hoursu_until_lunch


    def notify(self):
        lunch_start = '2020-05-05T12:00:00'
        duration = 60

        lunch_start_iso = datetime.fromisoformat(lunch_start)
        lunch_timestamp = datetime.timestamp(lunch_start_iso)

        hours_until_lunch = self.time_diff_in_hours(lunch_start_iso, datetime.now())

        if(hours_until_lunch < 3):
            True
        else:
            False
        # TODO if lunchbreak is in the next three hours



if __name__ == '__main__':
        lb = Lunchbreak('Stuttgart')

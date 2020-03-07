from services.weatherAPI.weather_service import WeatherAdapter
from services.weatherAPI.test.test_service import WeatherMock
from services.yelp.yelp_service import YelpService
from services.yelp.test.test_service import YelpMock
from datetime import datetime
from services.preferences import PrefService

class Lunchbreak:
    location = {'latitude': 48.765337599999995,
                'longitude': 9.161932799999999}

    def __init__(self, location, mock:bool=False):
        if mock:
            weather_adapter = WeatherAdapter.instance()
            weather_adapter.set_remote(WeatherMock())
            yelp_service = YelpService.instance()
            yelp_service.set_remote(YelpMock())
        #self.triggerUseCase(location)

    def trigger_use_case(self, location):
        self.check_lunch_options(location)
        #TODO send restaurants to controller and get user choice
        choice = self.wait_for_user_request()
        self.open_maps_route(choice)


    def check_lunch_options(self, location):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        lunch_start = '2020-03-03T12:00:00'
        duration = 60

        lunch_start_iso = datetime.fromisoformat(lunch_start)
        lunch_timestamp = datetime.timestamp(lunch_start_iso)

        hours_until_lunch = self.time_diff_in_hours(lunch_start_iso, datetime.now())

        ### get current location ###
        # TODO translate coordinates into an address
        location = 'Paulinenstraße 50, 70178 Stuttgart'
        city = 'Stuttgart'

        ### Check Weather ###
        weather_adapter = WeatherAdapter.instance()
        weather_adapter.update(city)
        will_be_bad_weather = weather_adapter.will_be_bad_weather(hours_until_lunch)

        ### suggest 10 nearest restaurants that meet preferences ###
        yelp_service = YelpService.instance()
        yelp_service.set_location(location)
        yelp_service.set_time(lunch_timestamp)
        yelp_service.set_radius(duration, will_be_bad_weather)
        yelp_service.set_radius(500, False)
        yelp_service.setLimit(50)

        yelp_service.request_businesses()

        self.restaurants = yelp_service.get_short_information_of_restaurants()
        for x in self.restaurants:
            print(x['name'])
        return self.restaurants


    def open_maps_route(self, choice):
        address = self.restaurants[choice]['address']
        ###Generate Maps Link

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
        lunch_start = '2020-03-03T12:00:00'
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

from services.weatherAPI.weather_service import WeatherAdapter
from services.weatherAPI.test.test_service import WeatherMock,WeatherAdapterRemote
from services.yelp.yelp_service import YelpService
from services.yelp.test.test_service import YelpMock, YelpServiceRemote
from datetime import datetime
from services.preferences import PrefService
from services.maps.geocoding_service import GeocodingJSONRemote
from services.maps.test.test_service import GeocodingMockRemote
from services.maps import MapService, GeocodingService, GeocodingRemote
from services.yelp.yelp_request import YelpRequest
from services.cal.cal_service import CalService, iCloudCaldavRemote, Event,CaldavRemote
from services.cal.test.test_service import CaldavMockRemote
import pytz
import re
from controller.notification_handler import Notification, NotificationHandler

class Lunchbreak:
    restraurants = None
    start = None
    end = None

    calender_remote = None

    def __init__(self, mock:bool=False):
        if mock:
            # self.set_WeatherApapter(WeatherMock())
            # self.set_calender(CaldavMockRemote())
            # self.set_geolocation(GeocodingMockRemote.instance())
            # self.set_YelpAdapter(YelpMock())
            weather_adapter = WeatherAdapter.instance()
            weather_adapter.set_remote(WeatherMock())
            yelp_service = YelpService.instance()
            yelp_service.set_remote(YelpMock())
            geocoding = GeocodingService.instance()
            geocoding.remote = GeocodingMockRemote.instance()
            self.calender_remote = CaldavMockRemote()
        else:
            geocoding = GeocodingService.instance()
            geocoding.remote = GeocodingJSONRemote.instance()
            self.calender_remote = iCloudCaldavRemote()

    def set_WeatherApapter(self, weather_adapter:WeatherAdapterRemote):
        weather_adapter = WeatherAdapter.instance()
        weather_adapter.set_remote(weather_adapter)

    def set_YelpAdapter(self, yelp_adapter:YelpServiceRemote):
        yelp_service = YelpService.instance()
        yelp_service.set_remote(yelp_adapter)

    def set_calender(self, calender:CaldavRemote):
        self.calender_remote = calender

    def set_geolocation(self, geolocation_remote:GeocodingRemote):
        geocoding = GeocodingService.instance()
        geocoding.remote = geolocation_remote

    def advance(self, message):
        if not self.restaurants:
            restaurants, start, end = self.check_lunch_options(message['location'] )
            return {'message' : self.restaurants}
        else:
            choice = self.wait_for_user_request(message)
            link = self.open_maps_route(message['location'], self.restaurants[choice])
            self.create_cal_event(self.start, self.end, self.restaurants[choice], link)

            #Reset if usecases are singletions
            self.restaurants = self.start = self.end = None
            return {'message': link}


    def check_lunch_options(self, location:list):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        #Search for timeslot between 10 and 15 Oclock
        start = datetime.now(pytz.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        end = datetime.now(pytz.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        duration, self.lunch_start, self.lunch_end =  self.find_longest_timeslot_between_hours(start,end)
        #print("Your lunchbreak starts at "  + str(lunch_start) + ". You have " + str(duration) + "minutes until your next event")
        lunch_timestamp = datetime.timestamp(self.lunch_start)

        hours_until_lunch = self.time_diff_in_hours(self.lunch_start, datetime.now(pytz.utc))

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
        self.restaurants = yelp_service.get_short_information_of_restaurants(search_params)
        #for x in restaurants:
        #    print(x['name'])
        return self.restaurants, self.lunch_start, self.lunch_end


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
        cal_service = CalService(self.calender_remote)
        cal_service.add_event(lunch)
        return lunch

    def wait_for_user_request(self, data):
        ### Wait for user decision ###
        seletedRestaurant = -1
        options = [{"One": 1}, {"Two": 2}, {"Three": 3}, {"Four": 4}, {"Five" : 5}]
        for opts in options:
            match = re.search(str(list(opts.keys())[0]) , data, re.IGNORECASE)
            if(match):
                seletedRestaurant = int(list(opts.values())[0])
        if(seletedRestaurant == -1):
            print("Retry")
        else:
            return (seletedRestaurant-1)

    def time_diff_in_hours(self, date1, date2):
        time_until_lunch = date1 - date2
        days, seconds = time_until_lunch.days, time_until_lunch.seconds
        hoursu_until_lunch = days * 24 + seconds // 3600
        return hoursu_until_lunch


    def find_longest_timeslot_between_hours(self, search_start, search_end):
        cal_service = CalService(self.calender_remote)
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

    def create_proactive_notification(self):
        notification = Notification('Where would you like to have lunch?')
        notification.add_message('Check out the best restaurant nearby for lunch. Just open the Buerro PDA!')
        notification.set_body('Check out the best restaurant nearby for lunch. Just open the Buerro PDA!')
        notification_handler = NotificationHandler.instance()
        notification_handler.push(notification)

    def trigger_proactive_usecase(self, location):
        print("Check Lunchbreak Proactive")
        if(self.notify()):
            self.create_proactive_notification()
            self.advance({'location' :location})
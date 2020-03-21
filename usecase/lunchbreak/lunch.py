from datetime import datetime
import pytz
import re

from services import WeatherAdapter, YelpService, GeocodingService, \
    MapService, CalService
from services.cal import Event
from services.yelp.yelp_request import YelpRequest

from handler import Notification, NotificationHandler, LocationHandler

class Lunchbreak:
    restraurants = None
    start = None
    end = None

    def set_services(self,
                    weather_adapter:WeatherAdapter,
                    yelp_service:YelpService,
                    geocoding_service:GeocodingService,
                    map_service:MapService,
                    calendar_service:CalService):
        self.weather_adapter = weather_adapter
        self.yelp_service = yelp_service
        self.geocoding_service = geocoding_service
        self.map_service = map_service
        self.calendar_service = calendar_service

    def advance(self, message):
        if not self.weather_adapter:
            raise Exception("Set Services!")

        lat, lon = self.get_location()
        if not self.restaurants:
            restaurants, start, end = self.check_lunch_options((lat, lon))
            return {'message' : self.restaurants}
        else:
            choice = self.wait_for_user_request(message)
            link = self.open_maps_route(location, self.restaurants[choice])
            self.create_cal_event(self.start, self.end, self.restaurants[choice], link)

            #Reset if usecases are singletions
            self.restaurants = self.start = self.end = None
            return {'message': link}


    def check_lunch_options(self, location:tuple):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        #Search for timeslot between 10 and 15 Oclock
        start = datetime.now(pytz.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        end = datetime.now(pytz.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        duration, self.lunch_start, self.lunch_end =  self.find_longest_timeslot_between_hours(start,end)
        #print("Your lunchbreak starts at "  + str(lunch_start) + ". You have " + str(duration) + "minutes until your next event")
        lunch_timestamp = datetime.timestamp(self.lunch_start)

        hours_until_lunch = self.time_diff_in_hours(self.lunch_start, datetime.now(pytz.utc))

        (lat, lon) = location
        city = self.geocoding_service.get_city_from_coords([lat, lon])

        ### Check Weather ###
        self.weather_adapter.update(city)
        will_be_bad_weather = self.weather_adapter.will_be_bad_weather(hours_until_lunch)

        search_params = YelpRequest()
        search_params.set_coordinates(location)
        search_params.set_time(lunch_timestamp)
        search_params.set_radius(duration, will_be_bad_weather)

        self.restaurants = self.yelp_service.get_short_information_of_restaurants(search_params)
        #for x in restaurants:
        #    print(x['name'])
        return self.restaurants, self.lunch_start, self.lunch_end


    def open_maps_route(self, location, restaurant):
        coords_dest = restaurant['coordinates']
        link = self.map_service.get_route_link(location, coords_dest)
        return link

    def create_cal_event(self, start, end, restaurant, link):
        lunch = Event()
        lunch.set_title('Lunch at ' + restaurant['name'])
        lunch.set_location(restaurant['address'])
        lunch.add('description', "Route information: " + str(link) + "\nWebsite: " + restaurant['url'])
        lunch.set_start(start)
        lunch.set_end(end)
        self.calendar_service.add_event(lunch)
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
        time, before, after = self.calendar_service.get_max_available_time_between(
            search_start, search_end)
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
        notification_handler = NotificationHandler.instance().push(notification)

    def trigger_proactive_usecase(self):
        print("Check Lunchbreak Proactive")
        if(self.notify()):
            self.create_proactive_notification()
            self.advance({'message': 'proactive'})


    def get_location(self):
        lh = LocationHandler.instance()
        return lh.get()

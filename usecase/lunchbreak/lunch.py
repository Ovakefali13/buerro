from datetime import datetime
import pytz
import re

from services import WeatherAdapter, YelpService, GeocodingService, \
    MapService, CalService
from services.cal import Event
from services.yelp.yelp_request import YelpRequest

from handler import Notification, NotificationHandler, LocationHandler
from usecase.usecase import Usecase, Reply

class Lunchbreak(Usecase):
    restraurants = None
    start = None
    end = None
    lunch_set = None

    def set_services(self,
                     weather_adapter: WeatherAdapter,
                     yelp_service: YelpService,
                     geocoding_service: GeocodingService,
                     map_service: MapService,
                     calendar_service: CalService):
        self.weather_adapter = weather_adapter
        self.yelp_service = yelp_service
        self.geocoding_service = geocoding_service
        self.map_service = map_service
        self.calendar_service = calendar_service

    def advance(self, message):
        if not self.weather_adapter:
            raise Exception("Set Services!")

        coords = self.get_location()
        if not self.restaurants:
            restaurants, start, end, duration = self.check_lunch_options(coords)

            return_message = f"Your lunch starts at {start}. You have {duration} minutes until your next event starts. " \
                f"I looked up the best five restaurants near you. Where would you like to eat for lunch?"

            return_dict = self.prepare_restaurants_for_transmission(restaurants)
            return Reply({'message': return_message, 'dict': return_dict})
        else:
            choice = self.evaluate_user_request(message)
            link = self.open_maps_route(coords, self.restaurants[choice])
            self.create_cal_event(self.start, self.end, self.restaurants[choice], link)

            #Reset if usecases are singletions
            self.restaurants = self.start = self.end = None
            self.lunch_set = datetime.now(pytz.utc)
            return {'message': link}

    def is_finished(self):
        return (not self.restaurants)

    def check_lunch_options(self, location:list):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        #Search for timeslot between 10 and 15 Oclock
        start = datetime.now(pytz.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        end = datetime.now(pytz.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        self.duration, self.lunch_start, self.lunch_end =  self.find_longest_timeslot_between_hours(start,end)
        #print("Your lunchbreak starts at "  + str(lunch_start) + ". You have " + str(duration) + "minutes until your next event")
        lunch_timestamp = datetime.timestamp(self.lunch_start)

        hours_until_lunch = self.time_diff_in_hours(self.lunch_start, datetime.now(pytz.utc))

        city = self.geocoding_service.get_city_from_coords(location)

        ### Check Weather ###
        self.weather_adapter.update(city)
        will_be_bad_weather = self.weather_adapter.will_be_bad_weather(hours_until_lunch)

        search_params = YelpRequest()
        search_params.set_coordinates(location)
        search_params.set_time(lunch_timestamp)
        search_params.set_radius(self.duration, will_be_bad_weather)

        self.restaurants = self.yelp_service.get_short_information_of_restaurants(search_params)
        #for x in restaurants:
        #    print(x['name'])
        return self.restaurants, self.lunch_start, self.lunch_end, self.duration


    def open_maps_route(self, location, restaurant):
        coords_dest = restaurant['coordinates']
        link = self.map_service.get_route_link(location, tuple(coords_dest))
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

    def evaluate_user_request(self, data, restaurants):
        ### Wait for user decision ###
        seletedRestaurant = -1
        options = [{"One": 1}, {"Two": 2}, {"Three": 3}, {"Four": 4}, {"Five" : 5}]
        for opts in options:
            match = re.search(str(list(opts.keys())[0]) , data, re.IGNORECASE)
            if(match):
                seletedRestaurant = int(list(opts.values())[0])
        if(seletedRestaurant == -1):
            print("Retry")

            # Try names
            r_names = self.prepare_restaurants_for_transmission(restaurants)
            for opts in r_names:
                match = re.search(str(list(opts.values())[0]), data, re.IGNORECASE)
                if (match):
                    seletedRestaurant = int(list(opts.keys())[0])
        else:
            return (seletedRestaurant-1)

    def time_diff_in_hours(self, date1, date2):
        time_until_lunch = date1 - date2
        days, seconds = time_until_lunch.days, time_until_lunch.seconds
        hoursu_until_lunch = days * 24 + seconds // 3600
        return hoursu_until_lunch


    def find_longest_timeslot_between_hours(self, search_start, search_end):
        time, before, after = self.calendar_service.get_max_available_time_between(search_start, search_end)
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

    def trigger_proactive_usecase(self):
        print("Check Lunchbreak Proactive")
        self.check_reset_usecase()
        if(self.lunch_set):
            if(self.notify()):
                self.create_proactive_notification()
                self.advance({'message': 'proactive'})


    def get_location(self):
        lh = LocationHandler.instance()
        return lh.get()


    def prepare_restaurants_for_transmission(self, restaurants):
        return_dict = {}
        for r in range(1,5):
            return_dict[r]:restaurants[r]['name']
        return return_dict


    def check_reset_usecase(self):
        if(self.lunch_set):
            now = datetime.now(pytz.utc)
            delta = now - self.lunch_set
            if (delta.days >= 1):
                self.lunch_set = None

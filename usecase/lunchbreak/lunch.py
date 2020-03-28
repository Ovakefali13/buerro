from datetime import datetime
import pytz
import re

from services import WeatherAdapter, YelpService, GeocodingService, \
    MapService, CalService
from services.cal import Event
from services.yelp.yelp_request import YelpRequest

from handler import Notification, NotificationHandler, LocationHandler, \
    UsecaseStore
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

    def set_default_services(self):
        self.weather_adapter = WeatherAdapter.instance()
        self.yelp_service = YelpService.instance()
        self.geocoding_service = GeocodingService.instance()
        self.map_service = MapService.instance()
        self.calendar_service = CalService.instance()

    def advance(self, message):
        if not hasattr(self, 'weather_adapter'):
            raise Exception("Set Services!")

<<<<<<< HEAD
        coords = self.get_location()
        if not self.restaurants:
            restaurants, start, end, duration = self.check_lunch_options(coords)
=======
        lat, lon = self.get_location()
        if not hasattr(self, 'restaurants') or not self.restaurants or message == 'proactive':
            if not hasattr(self, 'restaurants') or not self.restaurants:
                self.check_lunch_options((lat, lon))

            if len(self.restaurants) == 0:
                return Reply("No restaurants found in your area.")
>>>>>>> dfa40f932732181cfd93ef8add157f4eef4c8ad8

            return_message = (f"Your lunch starts at {self.lunch_start}. "
                            f"You have {self.duration} minutes until your next event starts. "
                            f"I looked up the best five restaurants near you. "
                            "Where would you like to eat for lunch?")

            return_dict = self.prepare_restaurants_for_transmission(self.restaurants)
            return Reply({'message': return_message, 'dict': return_dict})
        else:
<<<<<<< HEAD
            choice = self.evaluate_user_request(message)
            link = self.open_maps_route(coords, self.restaurants[choice])
            self.create_cal_event(self.start, self.end, self.restaurants[choice], link)
=======
            choice = self.evaluate_user_request(message, self.restaurants)
            if choice is None:
                return Reply(("I could not match your answer to any restaurant. "
                              "Please try again."))

            link = self.open_maps_route((lat, lon), self.restaurants[choice])
            self.create_cal_event(self.lunch_start, self.lunch_end, self.restaurants[choice], link)
>>>>>>> dfa40f932732181cfd93ef8add157f4eef4c8ad8

            # Reset
            self.restaurants = self.start = self.end = None
            self.lunch_set = datetime.now(pytz.utc)
            return Reply({'message': "With this link you can navigate there: ",
                        'link': link})

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

        ### Check Weather ###
        self.weather_adapter.update(coordinates=location)
        will_be_bad_weather = self.weather_adapter.will_be_bad_weather(hours_until_lunch)

        search_params = YelpRequest()
        search_params.set_coordinates(location)
        search_params.set_time(lunch_timestamp)
        search_params.set_radius(self.duration, will_be_bad_weather)

        self.restaurants = self.yelp_service.get_short_information_of_restaurants(search_params)
        return self.restaurants, self.lunch_start, self.lunch_end, self.duration

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

    def evaluate_user_request(self, message, restaurants):
        selectedRestaurant = -1
        try:
            selectedRestaurant = int(message)
            if selectedRestaurant > 5: selectedRestaurant = 5
        except:
            pass # no number

            options = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five" : 5}
            for word, num in options.items():
                match = re.search(word, message, re.IGNORECASE)
                if(match):
                    selectedRestaurant = num

        if selectedRestaurant == -1:
            # Try names
            r_names = self.prepare_restaurants_for_transmission(restaurants)
            for num, r_name in r_names.items():
                match = re.search(r_name, message, re.IGNORECASE)
                if (match):
                    selectedRestaurant = num
                else:
                    # no restaurant found...
                    return None


        return (selectedRestaurant-1)

    def time_diff_in_hours(self, date1, date2):
        time_until_lunch = date1 - date2
        days, seconds = time_until_lunch.days, time_until_lunch.seconds
        hoursu_until_lunch = days * 24 + seconds // 3600
        return hoursu_until_lunch


    def find_longest_timeslot_between_hours(self, search_start, search_end):
        time, before, after = self.calendar_service.get_max_available_time_between(search_start, search_end)
        return int((time.total_seconds() / 60)), before, after

    def hours_until_lunch(self):
        start = datetime.now(pytz.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        end = datetime.now(pytz.utc).replace(hour=15, minute=0, second=0, microsecond=0)
        duration, lunch_start, lunch_end = self.find_longest_timeslot_between_hours(start, end)

        lunch_timestamp = datetime.timestamp(lunch_start)

        hours_until_lunch = self.time_diff_in_hours(lunch_start, datetime.now(pytz.utc))

    def create_proactive_notification(self, message):
        notification = Notification('Where would you like to have lunch?')
        notification.add_message(message)
        notification.set_body('Check out the best restaurant nearby for lunch. Just open the Buerro PDA!')
        notification_handler = NotificationHandler.instance()
        notification_handler.push(notification)

    def trigger_proactive_usecase(self):
        print("Check Lunchbreak Proactive")
        self.check_reset_usecase()
        if not self.lunch_set and self.hours_until_lunch() < 3:
            reply = self.advance('proactive')
            if 'No restaurants found' in reply.message:
                return
            self.create_proactive_notification(reply.to_html())
            UsecaseStore.instance().set_running(self)


    def get_location(self):
        lh = LocationHandler.instance()
        return lh.get()


    def prepare_restaurants_for_transmission(self, restaurants):
        return_dict = {}
        for r in range(1,5):
            if r <= len(restaurants):
                return_dict[r] = restaurants[r]['name']
        return return_dict


    def check_reset_usecase(self):
        if(self.lunch_set):
            now = datetime.now(pytz.utc)
            delta = now - self.lunch_set
            if (delta.days >= 1):
                self.lunch_set = None

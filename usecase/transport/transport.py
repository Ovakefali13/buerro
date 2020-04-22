from services.weatherAPI.weather_service import WeatherAdapter
from services.preferences import PrefService, PrefJSONRemote
from services.maps import GeocodingService, MapService
from services.vvs import VVSService, VVSEfaJSONRemote
from usecase import Usecase, Reply
from handler import LocationHandler
from util import link_to_html

from multiprocessing import Process
from datetime import datetime, timedelta
import re


class Transport(Usecase):
    req_info = {"Start": None, "Dest": None, "ArrDep": None, "Time": None}
    transport_info = {
        "Cycling": None,
        "Car": None,
        "Walking": None,
        "VVS": None,
        "WeatherBad": None,
    }
    transport_recommendation = {"Favorite": None, "Fastest": None, "Viable": []}
    finished = False

    def __init__(self):
        self.set_default_services()

    def set_default_services(
        self,
        pref_service: PrefService = PrefService(PrefJSONRemote()),
        map_service: MapService = MapService.instance(),
        vvs_service: VVSService = VVSService.instance(VVSEfaJSONRemote.instance()),
        geo_service: GeocodingService = GeocodingService.instance(),
        wea_service: WeatherAdapter = WeatherAdapter.instance(),
    ):
        self.pref_service = pref_service
        self.map_service = map_service
        self.vvs_service = vvs_service
        self.geo_service = geo_service
        self.wea_service = wea_service

        self.pref = pref_service.get_preferences("transport")

    def get_transport_mode(
        self,
        start: tuple,
        dest: tuple,
        arr_dep: str = "Dep",
        time: datetime = datetime.now(),
    ):

        self.req_info["Start"] = start
        self.req_info["Dest"] = dest
        self.req_info["ArrDep"] = arr_dep
        self.req_info["Time"] = time

        return self.advance(None)

    def advance(self, message):
        if self.finished:
            self.req_info = dict.fromkeys(self.req_info, None)
            self.transport_info = dict.fromkeys(self.transport_info, None)
            self.transport_recommendation = dict.fromkeys(
                self.transport_recommendation, None
            )
            self.transport_recommendation["Viable"] = []

            self.finished = False

        if not self.wea_service:
            raise Exception("Set Services!")

        if None in self.req_info.values():
            self.set_transport_parameters(message)
        if None in self.req_info.values():
            return Reply(
                {
                    "message": "Please specify at least where you want to go. Example: I want to travel from home to the university and arrive at 10 p.m.."
                }
            )

        if None in self.transport_info.values():
            self.get_transport_information()

        options = self.compare_transport_options()
        self.finished = True
        return options

    def is_finished(self):
        return self.finished

    def set_transport_parameters(self, message):
        special_locations = ["home", "work", "mainstation", "university"]

        def get_special_location(location: str):
            return tuple(self.pref.get(location + "_coords"))

        def get_datetime(time: str):
            strings = time.split()
            hours = int(strings[0])
            now = datetime.now()
            date = None

            if "hours" in strings:
                date = now + timedelta(hours=hours)
            elif "p.m." in strings:
                date = now.replace(hour=hours + 12, minute=0, second=0)
            elif "a.m." in strings:
                date = now.replace(hour=hours, minute=0, second=0)

            if date < now:
                date = date + timedelta(days=1)

            return date

        def get_location():
            lh = LocationHandler.instance()
            return lh.get()

        """ Regex tested with
        I want to travel from Stuttgart to Frankfurt and arrive at 4 p.m.
        Now I want to travel to Frankfurt
        I want to travel from home to the university and arrive at 10 p.m.
        I want to travel from the mainstation to home in 2 hours
        I want to travel home now
        I want to travel home at 6 p.m. 
        I want to travel to Stuttgart and depart at 7 a.m.
        I want to travel from the mainstation to home
        """

        if not self.req_info["Start"]:
            regex = r"((?<=from\sthe\s)|(?<=from\s(?!the)))(\w*|home)"
            start = re.search(regex, message)
            if start:
                start = start[0]

            if start:
                if start in special_locations:
                    self.req_info["Start"] = get_special_location(start)
                else:
                    self.req_info["Start"] = self.geo_service.get_coords_from_address(
                        start
                    )
            else:
                self.req_info["Start"] = get_location()

        if not self.req_info["Dest"]:
            p = re.compile(
                r"((?<=to\sthe\s)|(?<=to\s(?!(the|arrive|travel))))(\w*|home)|(?<=travel\s)home"
            )
            dest = p.search(message)

            if dest:
                dest = dest[0]

            if dest:
                if dest in special_locations:
                    self.req_info["Dest"] = get_special_location(dest)
                else:
                    self.req_info["Dest"] = self.geo_service.get_coords_from_address(
                        dest
                    )

        if not self.req_info["ArrDep"]:
            p = re.compile(r"arrive(d)? at")
            arr_dep = p.search(message)
            if arr_dep:
                arr_dep = arr_dep[0]

            if arr_dep:
                self.req_info["ArrDep"] = "Arr"
            else:
                self.req_info["ArrDep"] = "Dep"

        if not self.req_info["Time"]:
            p = re.compile(r"(?<=at\s)\d{1,2}\s(a.m.|p.m.)|\d{1,2}\shours")
            time = p.search(message)
            if time:
                time = time[0]

            if time:
                self.req_info["Time"] = get_datetime(time)
            else:
                self.req_info["Time"] = datetime.now()

    def get_transport_information(self):
        start_coords = self.req_info.get("Start")
        dest_coords = self.req_info.get("Dest")

        def weather_service(self):
            self.wea_service.update(self.geo_service.get_city_from_coords(start_coords))
            self.transport_info["WeatherBad"] = self.wea_service.is_bad_weather()

        def map_service(self, name, mode):
            self.transport_info[name] = self.map_service.get_route_summary(
                start_coords, dest_coords, mode
            )

        def vvs_service(self):
            start = self.geo_service.get_address_from_coords(start_coords)
            dest = self.geo_service.get_address_from_coords(dest_coords)
            arr_dep = self.req_info.get("ArrDep")
            time_ = self.req_info.get("Time")
            journeys = self.vvs_service.get_journeys(start, dest, arr_dep, time_)

            self.transport_info["VVS"] = sorted(
                journeys, key=lambda x: x.get_duration()
            )[0]

        def runInParallel(*fns):
            proc = []
            for fn in fns:
                p = Process(target=fn)
                p.start()
                proc.append(p)
            for p in proc:
                p.join()

        runInParallel(
            weather_service(self),
            map_service(self, "Car", "driving-car"),
            vvs_service(self),
        )

        # Only request walking and cycling if distance is under a certain level
        # Would be better to use the euclidean distance, but that would need a new API -> expensive
        distance = self.transport_info["Car"]["distance"]
        if distance <= 30000:
            map_service(self, "Cycling", "cycling-regular")
        if distance <= 5000:
            map_service(self, "Walking", "foot-walking")

    def compare_transport_options(self):
        def create_link(mode: str):
            if mode == "VVS":
                return vvs.to_link()
            else:
                return self.map_service.get_route_link(
                    self.req_info.get("Start"), self.req_info.get("Dest"), mode
                )

        def print_duration(seconds: int):
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            string = ""
            if hours > 0:
                string = f"{int(hours)} hours "
            if minutes > 0:
                string = string + f"{int(minutes)} minutes and "
            string = string + f"{int(seconds)} seconds"
            return string

        viable = self.transport_recommendation.get("Viable")
        cycling = self.transport_info.get("Cycling")
        walking = self.transport_info.get("Walking")
        vvs = self.transport_info.get("VVS")
        car = self.transport_info.get("Car")
        vvs_duration = None
        walking_duration = None
        cycling_duration = None
        car_duration = None

        # Check if mode of travel exist
        if vvs is not None:
            viable.append("VVS")
            vvs_duration = vvs.get_duration().total_seconds()
        if cycling is not None:
            viable.append("cycling")
            cycling_duration = cycling.get("duration")
        if walking is not None:
            viable.append("walking")
            walking_duration = walking.get("duration")
        if car is not None:
            viable.append("car")
            car_duration = car.get("duration")
        if not viable:
            return Reply({"message": f"This route is not available."})

        # Check if weather is good
        if self.transport_info.get("WeatherBad"):

            if "cycling" in viable:
                viable.remove("cycling")
            if "walking" in viable:
                viable.remove("walking")

        # Check if there is enough time to get to the destination in time
        if self.req_info.get("ArrDep") == "Arr":
            time_left = (self.req_info.get("Time") - datetime.now()).total_seconds()

            if "cycling" in viable and cycling_duration > time_left:
                viable.remove("cycling")
            if "walking" in viable and walking_duration > time_left:
                viable.remove("walking")
            if "car" in viable and car_duration > time_left:
                viable.remove("car")
            if "VVS" in viable and vvs_duration > time_left:

                viable.remove("VVS")

            if not viable:
                # TODO provide alternatives
                return Reply(
                    {"message": f"There is not enough time to get to this destination."}
                )

        # Get prefered modes of travel
        walk_or_bike = self.pref.get("walk_or_bike")
        vvs_or_car = self.pref.get("vvs_or_car")

        if vvs_or_car in viable:
            self.transport_recommendation["Favorite"] = vvs_or_car
        # Set walk or bike first because it is healthy ;)
        if walk_or_bike in viable:
            self.transport_recommendation["Favorite"] = walk_or_bike

        # Get fastest mode of travel
        durations_sorted = {
            k: v
            for k, v in sorted(
                {
                    "cycling": cycling_duration if cycling_duration else 999999999,
                    "walking": walking_duration if walking_duration else 999999999,
                    "car": car_duration,
                    "VVS": vvs_duration,
                }.items(),
                key=lambda item: item[1],
            )
        }

        fastest = self.transport_recommendation["Fastest"] = list(
            durations_sorted.keys()
        )[0]
        favorite = self.transport_recommendation.get("Favorite")
        fastest_duration = durations_sorted.get(fastest)
        favorite_duration = durations_sorted.get(favorite)

        if favorite in viable:
            reply_dict = {
                "message": f'For this trip your prefered mode of transport {favorite} is available. It will take {print_duration(favorite_duration)}. {link_to_html(create_link(favorite), "Route Link")}'
            }
            duration = favorite_duration
        else:
            reply_dict = {
                "message": f'For this trip the mode of transport {fastest} is advised. It will take {print_duration(fastest_duration)}. {link_to_html(create_link(fastest), "Route Link")}'
            }
            duration = fastest_duration

        if self.req_info.get("ArrDep") is "Arr":
            dep_time = self.req_info.get("Time") - timedelta(seconds=duration)
            reply_dict["message"] = (
                reply_dict["message"]
                + f' You need to leave at {dep_time.strftime("%H:%M")}.'
            )

        if favorite and favorite != fastest:
            reply_dict["message"] = (
                reply_dict["message"]
                + f' However, the mode {fastest} is faster by {print_duration(favorite_duration - fastest_duration)}. {link_to_html(create_link(fastest), "Faster Route Link")}'
            )

        return Reply(reply_dict)

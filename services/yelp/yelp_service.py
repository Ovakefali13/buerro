import requests
import os
from abc import ABC, abstractmethod

from util import Singleton
from services.ApiError import ApiError
from services.preferences import PrefService
from services.yelp.yelp_request import YelpRequest


class YelpServiceModule(ABC):
    @abstractmethod
    def request_businesses(self, search_param):
        pass

    @abstractmethod
    def request_business(self, id: int):
        pass


@Singleton
class YelpServiceRemote(YelpServiceModule):
    API_TOKEN = os.getenv("YELP_API_KEY")
    headers = {
        "Authorization": "Bearer %s" % API_TOKEN,
    }

    def request_businesses(self, search_param):
        req = "https://api.yelp.com/v3/businesses/search"
        response = requests.request(
            "GET", req, headers=self.headers, params=search_param
        )
        if response.status_code != 200:
            raise ApiError("GET /tasks/ {}".format(response.status_code))
            print("Error")
        return response.json()

    def request_business(self, id):
        req = "https://api.yelp.com/v3/businesses/" + id
        response = requests.request("GET", req, headers=self.headers)
        if response.status_code != 200:
            raise ApiError("GET /tasks/ {}".format(response.status_code))
            print("Error")
        return response.json()


@Singleton
class YelpService:
    remote = None
    pref = None

    def __init__(self, remote: YelpServiceModule = None):
        if remote:
            self.remote = remote
        else:
            self.remote = YelpServiceRemote.instance()
        self.pref = PrefService()

    def set_remote(self, remote):
        self.remote = remote

    def get_businesses(self, req: YelpRequest):
        restaurants = self.remote.request_businesses(req.get_search_param())
        return restaurants

    def get_business(self, id):
        focused_restaurant = self.remote.request_business(id)
        return focused_restaurant

    def get_short_information_of_restaurants(self, req: YelpRequest):
        restaurants = self.remote.request_businesses(req.get_search_param())
        name_list = []
        for x in restaurants["businesses"]:
            info = {
                "name": x["name"],
                "id": x["id"],
                "price": x["price"],
                "is_closed": x["is_closed"],
                "rating": x["rating"],
                "address": x["location"]["address1"]
                + ", "
                + x["location"]["zip_code"]
                + " "
                + x["location"]["city"],
                "city": x["location"]["city"],
                "url": x["url"],
                "coordinates": [
                    x["coordinates"]["latitude"],
                    x["coordinates"]["longitude"],
                ],
            }
            name_list.append(info)
        return name_list

    def get_next_business(self, req: YelpRequest):
        restaurants = self.remote.request_businesses(req.get_search_param())
        info = {
            "name": restaurants["businesses"][0]["name"],
            "id": restaurants["businesses"][0]["id"],
            "phone": restaurants["businesses"][0]["phone"],
            "address": restaurants["businesses"][0]["location"]["address1"]
            + ", "
            + restaurants["businesses"][0]["location"]["zip_code"]
            + " "
            + restaurants["businesses"][0]["location"]["city"],
            "url": restaurants["businesses"][0]["url"],
        }
        return info

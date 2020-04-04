from abc import ABC, abstractmethod
import os
from opencage.geocoder import OpenCageGeocode, InvalidInputError, RateLimitExceededError, UnknownError
from util import Singleton
from services.preferences import PrefService, PrefJSONRemote

class GeocodingRemote(ABC):
    @abstractmethod
    def get_information_from_address(self, address:str):
        pass
    @abstractmethod
    def get_information_from_coords(self, coords:list):
        pass

@Singleton
class GeocodingJSONRemote(GeocodingRemote):

    def __init__(self):
        pref_service = PrefService(PrefJSONRemote())
        prefs = pref_service.get_preferences("transport")
        self.geocoder = OpenCageGeocode(os.environ['OPENCAGEGEOCODING_API_KEY'])


    # Street, City, Country
    def get_information_from_address(self, address:str):
        try:
            return self.geocoder.geocode(address, pretty=True)
        except RateLimitExceededError as ex:
            print(ex)


    def get_information_from_coords(self, coords:tuple):
        try:
            return self.geocoder.reverse_geocode(coords[0], coords[1], language='de', no_annotations='1')
        except RateLimitExceededError as ex:
            print(ex)

@Singleton
class GeocodingService:

    def __init__(self, remote:GeocodingRemote=GeocodingJSONRemote.instance()):
        self.remote = remote

    def get_coords_from_address(self, address:str):
        # filter blank strings
        if address:
            results = self.remote.get_information_from_address(address)[0]['geometry']
            latitude  = results.get('lat')
            longitude = results.get('lng')

            return latitude, longitude


    def get_address_from_coords(self, coords:tuple):
        results = self.remote.get_information_from_coords(coords)[0]['components']        
        street = results.get('road') or results.get('pedestrian')
        house_number = results.get('house_number')
        postcode = results.get('postcode')
        town = results.get('city') or results.get('village')

        return ' '.join(filter(None, (street, house_number, postcode, town)))


    def get_city_from_coords(self, coords:tuple):
        results = self.remote.get_information_from_coords(coords)[0]['components']

        return results.get('city') or results.get('village')

from abc import ABC, abstractmethod
from opencage.geocoder import OpenCageGeocode, InvalidInputError, RateLimitExceededError, UnknownError
from services.Singleton import Singleton
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
        self.geocoder = OpenCageGeocode(prefs['opencagegeocodingAPIKey'])


    # Street, City, Country
    def get_information_from_address(self, address:str):
        try:
            return self.geocoder.geocode(address, pretty=True)
        except RateLimitExceededError as ex:
            print(ex)


    def get_information_from_coords(self, coords:list):
        try:
            return self.geocoder.reverse_geocode(coords[0], coords[1], language='de', no_annotations='1')
        except RateLimitExceededError as ex:
            print(ex)

@Singleton
class GeocodingService:
    

    def __init__(self, remote:GeocodingRemote=GeocodingJSONRemote.instance()):
        self.remote = remote


    def get_coords_from_address(self, address:str):
        results = self.remote.get_information_from_address(address)
        latitude  = results[0]['geometry']['lat']
        longitude = results[0]['geometry']['lng']

        return [latitude, longitude]        


    def get_address_from_coords(self, coords:list):            
        results = self.remote.get_information_from_coords(coords)
        
        return results[0]['formatted']


    def get_city_from_coords(self, coords:list):
        results = self.remote.get_information_from_coords(coords)

        return results[0]['components']['city']


from abc import ABC, abstractmethod
from opencage.geocoder import OpenCageGeocode, InvalidInputError, RateLimitExceededError, UnknownError
from services.Singleton import Singleton

class GeocodingRemote(ABC):
    @abstractmethod
    def get_information_from_address(self, address):
        pass
    @abstractmethod
    def get_information_from_coords(self, coords):
        pass

@Singleton
class GeocodingJSONRemote(GeocodingRemote):
    # 2500 free transactions per day https://opencagedata.com
    API_TOKEN = '2642206c773e4b06aedabd0a0e876a2f'

    def __init__(self):
        self.geocoder = OpenCageGeocode(self.API_TOKEN)

    # Street, City, Country
    def get_information_from_address(self, address):
        try:
            return self.geocoder.geocode(address, pretty=True)
        except RateLimitExceededError as ex:
            print(ex)

    def get_information_from_coords(self, coords):
        try:
            return self.geocoder.reverse_geocode(coords[0], coords[1], language='de', no_annotations='1')
        except RateLimitExceededError as ex:
            print(ex)


class GeocodingService:

    def __init__(self, remote):
        self.remote = remote

    def get_coords_from_address(self, address):
        results = self.remote.get_information_from_address(address)
        latitude  = results[0]['geometry']['lat']
        longitude = results[0]['geometry']['lng']

        return [latitude, longitude]        

    def get_address_from_cords(self, coords):            
        results = self.remote.get_information_from_coords(coords)
        
        return results[0]['formatted']


remote = GeocodingJSONRemote.instance()

dic = remote.get_information_from_address('Rotebühlplatz 41, 70178 Stuttgart, Deutschland')
f = open('FILE.txt','a')

for item in dic:
        f.write("%s\n" % item)
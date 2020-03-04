import requests
from opencage.geocoder import OpenCageGeocode

# 2500 free transactions per day https://opencagedata.com
API_TOKEN = '2642206c773e4b06aedabd0a0e876a2f'

geocoder = OpenCageGeocode(API_TOKEN)

# Street, City, Country
def getCoordsFromAddress(address):
    try:
        results = geocoder.geocode(address)

        longitude = results[0]['geometry']['lng']
        latitude  = results[0]['geometry']['lat']
        return [longitude, latitude]        
    except RateLimitExceededError as ex:
        print(ex)

def getAddressFromCoords(lon, lat):
    try:
        results = geocoder.reverse_geocode(lat, lon, language='de', no_annotations='1')
        if results and len(results):
            return results[0]['formatted']
    except RateLimitExceededError as ex:
        print(ex)
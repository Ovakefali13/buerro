import requests
from opencage.geocoder import OpenCageGeocode
# pip install opencage

# 2500 free transactions per day https://opencagedata.com
API_TOKEN = '2642206c773e4b06aedabd0a0e876a2f'

geocoder = OpenCageGeocode(API_TOKEN)

# Street, City, Country
def getCoordsFromAddress(address):
    results = geocoder.geocode(address)

    longitude = results[0]['geometry']['lng']
    latitude  = results[0]['geometry']['lat']

    return [longitude, latitude]



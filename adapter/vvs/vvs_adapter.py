
import urllib.request
from urllib.parse import urlencode, quote
import json
import sys
import os
from datetime import datetime, timedelta, timezone

from .journey import Journey

class VVSAdapter:

    event_buffer = timedelta(minutes=0)

    def __init__(self, event_buffer=timedelta(minutes=0)):
        self.event_buffer = event_buffer
    
    def get_station_id(self, station:str):
        base_url = "https://www3.vvs.de/mngvvs/XML_STOPFINDER_REQUEST?SpEncId=0&coordOutputFormat=EPSG:4326&outputFormat=rapidJSON&serverInfo=1&suggestApp=vvs&type_sf=any&version=10.2.10.139&name_sf="

        station_url = base_url + quote(station)
        contents = json.loads(urllib.request.urlopen(station_url).read())
        station_id = contents.get('locations')[0].get('id')
        return station_id

    def get_journeys(self, origin:str, dest:str, arr_dep:str, itd_time:str=datetime.now()):
        def format_daytime(itd_time:datetime):
            return itd_time.strftime("%H%M")

        origin_id = self.get_station_id(origin)
        dest_id = self.get_station_id(dest)
        itd_time = itd_time - self.event_buffer

        url = "https://www3.vvs.de/mngvvs/XML_TRIP_REQUEST2?SpEncId=0&changeSpeed=normal&computationType=sequence&coordOutputFormat=EPSG:4326&cycleSpeed=14&deleteAssignedStops=0&deleteITPTWalk=0&descWithElev=1&illumTransfer=on&imparedOptionsActive=1&itOptionsActive=1&language=de&locationServerActive=1&macroWebTrip=true&noElevationProfile=1&noElevationSummary=1&outputFormat=rapidJSON&outputOptionsActive=1&ptOptionsActive=1&routeType=leasttime&searchLimitMinutes=360&securityOptionsActive=1&serverInfo=1&showInterchanges=1&trITArrMOT=100&trITArrMOTvalue=15&trITDepMOT=100&trITDepMOTvalue=15&tryToFindLocalityStops=1&type_destination=any&type_origin=any&useElevationData=1&useLocalityMainStop=0&useRealtime=1&useUT=1&version=10.2.10.139&w_objPrefAl=12&w_regPrefAm=1"

        params = urlencode({
            'itdDate': datetime.now().strftime('%Y%m%d'),
            'itdDateTimeDepArr': arr_dep,
            'itdTime': format_daytime(itd_time),
            'itdTripDateTimeDepArr': arr_dep,
            'name_destination': dest_id,
            'name_origin': origin_id
        })

        contents = json.loads(urllib.request.urlopen(url + params).read())
        
        journeys = []
        for vvs_journey in contents.get('journeys'):
            journey = Journey()
            journey.from_vvs(vvs_journey)
            journeys.append(journey)

        return journeys


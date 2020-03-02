
import urllib.request
from urllib.parse import urlencode
import json
import sys
import os
from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod

from .journey import Journey

class VVSRemote(ABC):
   
    @abstractmethod
    def get_locations(self, location:str):
        pass

    @abstractmethod
    def get_journeys(self):
        pass


class VVSEfaJSONRemote(VVSRemote):
    base_url = "http://efastatic.vvs.de/vvs"
    
    base_params = {
        "outputFormat": "rapidJSON",
        "version": "10.2.10.139"
    }
    
    def get_locations(self, location:str):
        params = { **self.base_params,
            "type_sf": "any",
            "name_sf": location
        }
        url = self.base_url + "/XML_STOPFINDER_REQUEST?" + urlencode(params)
        # TODO error handling
        return json.loads(urllib.request.urlopen(url).read()).get('locations')
    
    def get_journeys(self, origin_id:str, dest_id:str, arr_dep:str, req_time:datetime):
        def format_daytime(itd_time:datetime):
            return itd_time.strftime("%H%M")

        params = { **self.base_params,
            "routeType": "leasttime",
            "type_destination": "any",
            "type_origin": "any",
            'itdDate': req_time.strftime('%Y%m%d'),
            'itdDateTimeDepArr': arr_dep,
            'itdTime': format_daytime(req_time),
            'itdTripDateTimeDepArr': arr_dep,
            'name_destination': dest_id,
            'name_origin': origin_id
        }

        url = self.base_url + "/XML_TRIP_REQUEST2?" + urlencode(params)
        # TODO error handling
        return json.loads(urllib.request.urlopen(url + params).read()).get('journeys')
        

"""
class VVAEfaXMLRemote(VVSRemote):
    base_url = "http://efastatic.vvs.de/vvs"
    outputFormat = "XML" 
"""
        

class VVSAdapter:

    event_buffer = timedelta(minutes=0)
    remote = None

    def __init__(self, remote, event_buffer=timedelta(minutes=0)):
        self.remote = remote
        self.event_buffer = event_buffer
    
    def get_location_id(self, location:str):
        best_match = list(filter(lambda l: l.get('isBest'),
            self.remote.get_locations(location)))[0]
        return best_match.get('id')

    def get_journeys(self, origin:str, dest:str, arr_dep:str, time:datetime=datetime.now()):
        origin_id = self.get_station_id(origin)
        dest_id = self.get_station_id(dest)
        time = time - self.event_buffer
        
        remote_journeys = remote.get_journeys(origin_id, dest_id, arr_dep, time)
        
        journeys = []
        for vvs_journey in remote_journeys:
            journey = Journey()
            journey.from_vvs(vvs_journey)
            journeys.append(journey)

        return journeys

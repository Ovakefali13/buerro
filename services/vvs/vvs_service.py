import requests
from urllib.parse import urlencode
import json
import sys
import os
from datetime import datetime as dt, timedelta, timezone
import pytz
from abc import ABC, abstractmethod

from util import Singleton
from . import Journey, JourneyRequest

class VVSRemote(ABC):
    @abstractmethod
    def get_locations(self, location:str):
        pass

    @abstractmethod
    def get_journeys(self, req:JourneyRequest):
        pass

@Singleton
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

        try:
            res = requests.get(url)
        except Exception as err:
            raise Exception("Error fetching VVS location: ", err)
        try:
            return res.json().get('locations')
        except:
            raise Exception("Response does not contain locations ", res)

    def get_journeys(self, req:JourneyRequest):

        params = { **self.base_params,
                **req.to_efa_params()
        }

        url = self.base_url + "/XML_TRIP_REQUEST2?" + urlencode(params)

        try:
            res = requests.get(url)
        except Exception as err:
            raise Exception("Error fetching VVS location: ", err)
        try:
            return res.json().get('journeys')
        except:
            raise Exception("Response does not contain journeys ", res)

@Singleton
class VVSService:

    def __init__(self, remote:VVSRemote = VVSEfaJSONRemote.instance()):
        self.remote = remote

    def set_remote(self, remote:VVSRemote):
        self.remote = remote

    def get_location_id(self, location:str):
        if not location:
            raise Exception("Passed an empty string as location")
        locations = self.remote.get_locations(location)
        if locations:
            best_match = list(filter(lambda l: l.get('isBest'),
                locations))[0]
            return best_match.get('id')
        else:
            raise Exception(f"Could not find a VVS stop matching {location}")

    def get_journeys(self, origin:str, dest:str,
        arr_dep:str, time:dt=dt.now(pytz.utc)):

        origin_id = self.get_location_id(origin)
        dest_id = self.get_location_id(dest)

        return self.get_journeys_for_id(origin_id, dest_id, arr_dep, time)

    def get_journeys_for_id(self, origin_id:str, dest_id:str,
        arr_dep:str, time:dt=dt.now(pytz.utc)):

        req = JourneyRequest(origin_id, dest_id, arr_dep, time)
        remote_journeys = self.remote.get_journeys(req)

        journeys = []
        for vvs_journey in remote_journeys:
            journey = Journey()
            journey.from_vvs(vvs_journey)
            journeys.append(journey)

        return journeys

    def recommend_journey_to_arrive_by(self, journeys, date:dt):
        def _time_from_date(journey, date):
            return date - journey.get_arr_time()

        """ three requirements for choosing a tram:
                1. I am on time
                2. I am not there too early (just on time)
                3. It doesn't take too long (advantage over others > 5 minutes)
            solution:
                1. filter such that none are too late
                2. sort in reverse order (latest to earliest)
                3. only consider ealier ones if they take significantly less time
        """
        none_too_late = list(filter(lambda journey:
            _time_from_date(journey, date) >= timedelta(0), journeys))
        sorted_by_arrival = sorted(none_too_late, reverse=True,
                key=lambda journey : journey.get_arr_time())

        recommended_journey = sorted_by_arrival[0]
        that_much_faster = timedelta(minutes=5)
        for journey in sorted_by_arrival:
            if(recommended_journey.get_duration() >= that_much_faster + journey.get_duration()):
                recommended_journey = journey

        return recommended_journey


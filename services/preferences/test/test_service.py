import unittest
from .. import PrefJSONRemote, PrefService, PrefRemote
import os
from datetime import datetime

class TestPrefService(unittest.TestCase):
    remote = PrefJSONRemote()
    pref_service = PrefService(remote)

    def test_get_apiKey(self):
        api_Key = self.pref_service.get_preferences('cooking')
        self.assertEqual(api_Key['general']['spoonacularAPIKey'], '0a3a6b562932438aaab0cb05460096de')
    def test_merge_Json_Files(self):
        json1 = {
            'general1': 'prefGeneral1',
        }
        json2 = {
		    "cooking1": "prefCooking1",
		    "cooking2": "prefCooking2"
	    }
        rightJson = {
            'general1': 'prefGeneral1',
		    "cooking1": "prefCooking1",
		    "cooking2": "prefCooking2"
	    }
        mergedJson = self.remote.merge_Json_Files(json1, json2)
        self.assertEqual(rightJson, mergedJson)
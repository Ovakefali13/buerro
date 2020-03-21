import unittest
from .. import PrefJSONRemote, PrefService, PrefRemote
import os
from datetime import datetime

class TestPrefService(unittest.TestCase):
    remote = PrefJSONRemote()
    pref_service = PrefService(remote)

    def test_get_apiKey(self):
        api_Key = self.pref_service.get_preferences("cooking")
        self.assertEqual(api_Key["spoonacularAPIKey"], "0a3a6b562932438aaab0cb05460096de")
    def test_merge_json_files(self):
        json1 = {
            "general1": "prefGeneral1",
        }
        json2 = {
            "cooking1": "prefCooking1",
            "cooking2": "prefCooking2"
        }
        rightJson = {
            "general1": "prefGeneral1",
            "cooking1": "prefCooking1",
            "cooking2": "prefCooking2"
        }
        mergedJson = self.remote.merge_json_files(json1, json2)
        self.assertEqual(rightJson, mergedJson)
    
    def test_get_specific_pref(self):
        self.assertEqual(self.pref_service.get_specific_pref("spoonacularAPIKey"), "0a3a6b562932438aaab0cb05460096de")

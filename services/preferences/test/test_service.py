import unittest
from .. import PrefJSONRemote, PrefService, PrefRemote
import os
from datetime import datetime

class TestPrefService(unittest.TestCase):
    remote = PrefJSONRemote()
    pref_service = PrefService(remote)

    def test_get_apiKey(self):
        api_Key = self.pref_service.get_preferences("cooking")
        self.assertIsInstance(api_Key["diet"], str)
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
        self.assertIsInstance(
            self.pref_service.get_specific_pref("maxCookingTime"),
            int)

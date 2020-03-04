import services.preferences.pref_service as pa
import services.preferences.test.test_service as pa_test

test = pa.PrefService(pa.PrefJSONRemote())
print(test.get_preferences("cooking"))

unitTest = pa_test.TestPrefService()
print(unitTest.test_get_apiKey)
print(unitTest.test_merge_Json_Files)
import services.preferences.preferences_adapter as pa

test = pa.PrefService(pa.PrefJSONRemote())
print(test.get_preferences("cooking"))
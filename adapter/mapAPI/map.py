import requests

# 2500 free transactions per day
API_TOKEN = 'N27kv6AwYWkFy2BR0ApNAKg5pEPA9BiU'

def getRouteSummaryFromTo(startCord, destCord, extraargs = ['travelMode=car', 'traffic=true', 'routeRepresentation=summaryOnly']):
    req = 'https://api.tomtom.com/routing/1/calculateRoute/' + startCord + ':' + destCord + '/' + 'json?' + '&'.join(extraargs) + '&' + 'key=' +  API_TOKEN  

    exit
    print(req)
    resp = requests.get(req)
    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('GET /tasks/ {}'.format(resp.status_code))
        print('Error')
    print(resp.json())

    routeData = resp.json()

    for name, value in routeData['routes'][0]['summary'].items():
        print(f"{name}: {value}")

    return routeData

getRouteSummaryFromTo('49.066996,9.297045', '48.814231,9.170677')
import requests
from geocoding import getCoordsFromAddress

# 2500 free transactions per day https://developer.tomtom.com/
API_TOKEN = 'N27kv6AwYWkFy2BR0ApNAKg5pEPA9BiU'

def getRouteSummaryFromTo(start, dest, extraargs = ['routeRepresentation=summaryOnly']):
    req = 'https://api.tomtom.com/routing/1/calculateRoute/' + getCoordsFromAddress(start) + ':' + getCoordsFromAddress(dest) + '/' + 'json?key=' +  API_TOKEN + '&' + '&'.join(extraargs)

    resp = requests.get(req)
    if resp.status_code != 200:
        # This means something went wrong.
        print('Error:', resp.status_code)

    routeData = resp.json()

    return routeData


def test():
    route = getRouteSummaryFromTo('Lindenstraße 31-1, Abstatt', 'Stuttgart')

    for name, value in route['routes'][0]['summary'].items():
        print(f"{name}: {value}")
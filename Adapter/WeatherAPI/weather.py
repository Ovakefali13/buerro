import requests


API_TOKEN = '716b047d4b59fba6550709d60756b0fd'


def getCurrentWeatherByCity(city):
    req = 'https://api.openweathermap.org/data/2.5/weather?q=' +  city + '&appid=' + API_TOKEN
    print(req)
    resp = requests.get(req)
    if resp.status_code != 200:
        # This means something went wrong.
        #raise ApiError('GET /tasks/ {}'.format(resp.status_code))
        print('Error')
    print(resp.json())
    weatherData = resp.json()
    print(weatherData['weather'][0]['main'])
    print(weatherData['main']['temp'])
    return weatherData


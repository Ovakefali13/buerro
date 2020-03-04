from services.weatherAPI.WeatherAdapter import WeatherAdapter
from services.yelp.yelp_service import YelpService
from datetime import datetime
from services.preferences import preferences_adapter

class Lunchbreak:
    location = {}

    def __init__(self, location):
        self.triggerUseCase(location)

    def triggerUseCase(self, location):
        self.checkLunchOptions(location)
        choice = self.waitForUserRequest()
        self.openMapsRoute(choice)


    def checkLunchOptions(self, location):
        ### Search Calender for timeslot sufficent for a lunchbreak ###
        lunchStart = '2020-03-03T12:00:00'
        duration = 60

        lunchStartIso = datetime.fromisoformat(lunchStart)
        lunchTimestamp = datetime.timestamp(lunchStartIso)

        hoursUntilLunch = self.timeDiffInHours(lunchStartIso, datetime.now())

        ### get current location ###
        location = 'Paulinenstraße 50, 70178 Stuttgart'
        city = 'Stuttgart'

        ### Check Weather ###
        weatherAdapter = WeatherAdapter.instance()
        weatherAdapter.update(city)
        willBeBadWeather = weatherAdapter.willBeBadWeather(hoursUntilLunch)

        ### suggest 10 nearest restaurants that meet preferences ###
        yelpService = YelpService.instance()
        yelpService.setLocation(location)
        yelpService.setTime(lunchTimestamp)
        yelpService.setRadius(duration, willBeBadWeather)
        yelpService.requestBusinesses()

        self.restaurants = yelpService.getShortInformationOfRestaurants()
        for x in self.restaurants:
            print(x['name'])

    def openMapsRoute(self, choice):
        address = self.restaurants[choice]['address']
        ###Generate Maps Link

    def waitForUserRequest(self):
        ### Wait for user decision ###
        seletedRestaurant = 2
        return seletedRestaurant

    def timeDiffInHours(self,date1, date2):
        timeUntilLunch = date1 - date2
        days, seconds = timeUntilLunch.days, timeUntilLunch.seconds
        hoursuUntilLunch = days * 24 + seconds // 3600
        return hoursuUntilLunch


if __name__ == '__main__':
        lb = Lunchbreak('Stuttgart')

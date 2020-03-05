class Recipe:
    location = {'latitude': 48.765337599999995,
                'longitude': 9.161932799999999}

    def __init__(self, location):
        self.triggerUseCase(location)

    def triggerUseCase(self, location):
        self.checkLunchOptions(location)
        choice = self.waitForUserRequest()
        self.openMapsRoute(choice)

    

    def checkLunchOptions(self, location):
        
    def openMapsRoute(self, choice):
        
    def waitForUserRequest(self):
        
    def timeDiffInHours(self,date1, date2):
    
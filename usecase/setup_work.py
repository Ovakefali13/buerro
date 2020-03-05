import Usecase, StateMachine
from services import CalService, VVSService#, TodoService, MusicService
from services import BaseCalService, BaseVVSService#, BaseTodoService, BaseMusicService
#from usecase import TransportUsecase
"""
        if self.count == 1:
            return {
                'message': "I created reminders for you. Do you want music?"
            }
        if self.count == 2:
            return {
                'message': 'How about this Spotify playlist?'
                    + '\nWhich project do you want to work on?',
                'link': 'https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ'
            }
        if self.count == 3:
            todos = [
                'Mark 1 to n relationships in architecture',
                'Implement a prototype for browser notifications'
            ]
            return {
                'message': "Here are you Todo's: ",
                'list': todos
            }
        raise Exception("advance called too often")
"""

@Singleton
class WorkSessionUsecase(Usecase):

    def __init__(self):
        self.fsm = StateMachine()

        self.calService = None
        self.vvsService = None
        # TODO self.transportUsecase = None
        self.todoService = None
        self.musicService = None

    def setCalService(service:BaseCalService):
        self.calService = service
    def setVVSService(service:BaseVVSService):
        self.vvsService = service

    def define_state_transitions(self):

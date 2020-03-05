import unittest
from .. import WorkSessionUsecase
from service import BaseCalService, BaseVVSService, BaseTodoService,
    BaseMusicService

@Singleton
class MockCalService(BaseCalService):
    pass

@Singleton
class MockVVSService(BaseVVSService):
    pass

@Singleton
class MockTodoService(BaseTodoService):
    pass

@Singleton
class MockMusicService(BaseMusicService):
    pass

class TestWorkSessionUsecase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        usecase = WorkSessionUsecase()
        usecase.setCalService(MockCalService.instance())
        usecase.setVVSService(MockVVSService.instance())
        usecase.setTodoService(MockTodoService.instance())
        usecase.setMusicService(MockMusicService.instance())
        self.usecase = usecase

   def test_advances_correctly(self):
         

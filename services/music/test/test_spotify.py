import unittest
import os
from urllib.parse import urlparse

from services.Singleton import Singleton
from .. import MusicRemote, SpotifyRemote, MusicService

@Singleton
class MockMusicRemote(MusicRemote):
    def get_playlist_for_mood(self, mood:str):
        return "https://open.spotify.com/playlist/37i9dQZF1DX576ecqLnVqL?si=xij5j2DsQwClphFotqa3dQ"


class TestMusicService(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.music_service = MusicService.instance()
        if 'DONOTMOCK' in os.environ:
            self.remote = SpotifyRemote.instance()
        else:
            self.remote = MockMusicRemote.instance()
        self.music_service.set_remote(self.remote)

    def test_can_get_playlist_link_for_mood(self):
        def uri_valid(x):
            try:
                result = urlparse(x)
                return all([result.scheme, result.netloc, result.path])
            except:
                return False
        uri = self.music_service.get_playlist_for_mood("focus")
        self.assertTrue(uri_valid(uri))

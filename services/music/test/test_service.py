import unittest
import os
from urllib.parse import urlparse

from util import Singleton
from .. import MusicRemote, SpotifyRemote, MusicService

@Singleton
class MusicMockRemote(MusicRemote):
    def get_playlist_for_mood(self, mood:str):
        uri = "https://open.spotify.com/playlist/37i9dQZF1DX576ecqLnVqL?si=xij5j2DsQwClphFotqa3dQ"
        return uri, "Test Playlist"

class TestMusicService(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.music_service = MusicService.instance(SpotifyRemote.instance())
        else:
            self.music_service = MusicService.instance(MusicMockRemote.instance())

    def test_can_get_playlist_link_for_mood(self):
        def uri_valid(x):
            try:
                result = urlparse(x)
                return all([result.scheme, result.netloc, result.path])
            except:
                return False
        uri, name = self.music_service.get_playlist_for_mood("focus")
        self.assertTrue(uri_valid(uri))
        self.assertIsInstance(name, str)

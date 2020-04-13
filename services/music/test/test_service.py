import unittest
import os
from urllib.parse import urlparse

from util import Singleton
from .. import MusicRemote, SpotifyRemote, MusicService, Playlist

@Singleton
class MusicMockRemote(MusicRemote):
    def get_category_for_mood(self, mood: str):
        if mood.lower() == "focus":
            return {"name": "focus",
                    "id": "abc"}
        return {}

    def get_playlists_for_category(self, category_id: str):
        if category_id == "abc":
            return [
                Playlist('123', 'Music for concentration', 'https://music.com/123'),
                Playlist('124', 'Piano music', 'https://music.com/124'),
            ]
        return []

    def get_user_playlists(self):
        return [
            Playlist('124', 'Piano music', 'https://music.com/124'),
            Playlist('125', 'Classic Rock', 'https://music.com/125'),
        ]

class TestMusicService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if 'DONOTMOCK' in os.environ:
            cls.music_service = MusicService.instance(SpotifyRemote.instance())
        else:
            cls.music_service = MusicService.instance(MusicMockRemote.instance())

    def test_can_get_playlist_link_for_mood(self):
        def uri_valid(uri):
            try:
                result = urlparse(uri)
                return all([result.scheme, result.netloc, result.path])
            except ValueError:
                return False

        playlist = self.music_service.get_playlist_for_mood("focus")
        self.assertIsInstance(playlist, Playlist)
        self.assertTrue(uri_valid(playlist.get_url()))
        self.assertIsInstance(playlist.get_name(), str)

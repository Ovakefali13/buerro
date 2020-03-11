import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from abc import ABC, abstractmethod
from os import environ
from dotenv import load_dotenv
import random
import concurrent.futures

from services.Singleton import Singleton

class MusicRemote(ABC):
    @abstractmethod
    def get_playlist_for_mood(self, mood:str):
        pass

@Singleton
class SpotifyRemote(MusicRemote):
        def __init__(self):
            load_dotenv()

            required_env = (
                'SPOTIPY_CLIENT_ID',
                'SPOTIPY_CLIENT_SECRET',
                'SPOTIFY_USERNAME'
            )

            if not all([var in environ for var in required_env]):
                raise EnvironmentError("Did not set all of these environment variables: ",
                    required_env)

            manager  = SpotifyClientCredentials()
            self.sp = spotipy.Spotify(client_credentials_manager=manager)
            self.username = environ['SPOTIFY_USERNAME']

        def get_playlist_for_mood(self, mood:str):
            def _request_user_playlists():
                offset = 0
                playlists = []
                while offset < 150:
                    answer = self.sp.user_playlists(user=self.username, limit=50, offset=offset)
                    playlists.extend(answer['items'])
                    if int(answer['total']) < 50:
                        return playlists
                    offset += 50

            def _request_categories(offset):
                return self.sp.categories(country='DE', locale='en', limit=20,
                    offset=offset)

            def _request_until_category_match(mood):
                offset = 0
                while offset < 100:
                    answer = _request_categories(offset)
                    categories = answer['categories']['items']

                    matches = list(
                        filter(lambda c: c['name'].lower() == mood.lower(), categories))

                    if matches:
                        return matches[0]

                    offset += 20
                return None

            with concurrent.futures.ThreadPoolExecutor() as executor:
                cat_future = executor.submit(_request_until_category_match, mood)
                up_future = executor.submit(_request_user_playlists)

                cat_match = cat_future.result()
                user_playlists = up_future.result()

            if cat_match:
                cat_playlists = self.sp.category_playlists(cat_match['id'])
                cat_playlists = cat_playlists['playlists']['items']

                shared_playlists = set(map(lambda p: p['id'], user_playlists)).intersection(
                    set(map(lambda p: p['id'], cat_playlists)))

                if shared_playlists:
                    playlist = random.choice(shared_playlists)
                else:
                    playlist = random.choice(cat_playlists)

            else:
                if user_playlists:
                    playlist = random.choice(user_playlists)

            if not playlist:
                raise Exception("Couldn't find any matching playlist")

            return playlist['external_urls']['spotify']

@Singleton
class MusicService:
    def __init__(self, remote=SpotifyRemote):
        self.remote = remote

    def set_remote(self, remote:MusicRemote):
        self.remote = remote

    def get_playlist_for_mood(self, mood:str):
        return self.remote.get_playlist_for_mood(mood)

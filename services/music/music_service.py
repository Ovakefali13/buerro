from abc import ABC, abstractmethod
import os
import random
import base64
from datetime import datetime as dt, timedelta
from urllib.parse import urlencode

import concurrent.futures
import requests

from util import Singleton
from services.preferences import PrefService

class MusicRemote(ABC):
    @abstractmethod
    def get_category_for_mood(self, mood: str):
        pass

    @abstractmethod
    def get_playlists_for_category(self, category_id: str):
        pass

    @abstractmethod
    def get_user_playlists(self):
        pass

class Playlist:
    def __init__(self, id_: str, name: str, url: str):
        self._id = id_
        self.name = name
        self.url = url

    @staticmethod
    def from_spotify(spotify_playlist):
        instance = Playlist(
            name=spotify_playlist['name'],
            url=spotify_playlist['external_urls']['spotify'],
            id_=spotify_playlist['id']
        )
        return instance

    def get_url(self):
        return self.url

    def get_id(self):
        return self._id

    def get_name(self):
        return self.name


@Singleton
class SpotifyRemote(MusicRemote):
    def __init__(self):

        required_env = (
            'SPOTIFY_CLIENT_ID',
            'SPOTIFY_CLIENT_SECRET',
            'SPOTIFY_USERNAME'
        )

        self.pref_service = PrefService()
        pref = self.pref_service.get_preferences('music')

        if not all([var in os.environ for var in required_env]):
            raise EnvironmentError("Did not set all of these environment variables: ",
                                   required_env)

        self.refresh_access_token()

        self.api_base='https://api.spotify.com/v1'

    def refresh_access_token(self):
        def _make_authorization_headers(client_id, client_secret):
            auth_header = base64.b64encode(
                str(client_id + ":" + client_secret).encode("ascii")
            )
            return {"Authorization": "Basic %s" % auth_header.decode("ascii")}

        client_id = os.environ['SPOTIFY_CLIENT_ID']
        client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

        headers = _make_authorization_headers(client_id, client_secret)

        token_api = "https://accounts.spotify.com/api/token"
        res = requests.post(token_api,
            headers=headers,
            data={"grant_type": "client_credentials"},
            verify=True)

        if res.status_code != 200:
            raise Exception("Failed to fetch Spotify Token: " + res.reason)

        res = res.json()
        self.access_token = res.get('access_token')
        self.token_expiry = dt.now() + timedelta(seconds=res.get('expires_in') - 60)

    def get_headers(self):
        if dt.now() >= self.token_expiry:
            self.refresh_access_token()
        return {
            'Authorization': f'Bearer {self.access_token}'
        }

    def get_user_playlists(self):

        username = os.environ['SPOTIFY_USERNAME']
        endpoint = self.api_base + f'/users/{username}/playlists'

        def _request_user_playlist(limit, offset):
            res = requests.get(endpoint,
                    headers=self.get_headers(),
                    params=urlencode({
                            'limit': limit,
                            'offset': offset
                    })
                )

            if res.status_code != 200:
                raise Exception("Failed to fetch user playlists: " + res.reason)
            return res.json()

        offset = 0
        playlists = []
        while offset < 150:
            answer = _request_user_playlist(limit=50, offset=offset)
            playlists.extend(answer['items'])
            if int(answer['total']) < 50:
                break
            offset += 50

        return list(map(Playlist.from_spotify, playlists))

    def get_category_for_mood(self, mood: str):
        def _get_categories(country, locale='en', limit=20, offset=0):
            endpoint = self.api_base+'/browse/categories'
            res = requests.get(endpoint,
                    headers=self.get_headers(),
                    params=urlencode({
                            'country': country,
                            'locale': locale,
                            'limit': limit,
                            'offset': offset
                    })
                )

            if res.status_code != 200:
                raise Exception("Failed to fetch spotify categories: " + res.reason)
            return res.json()['categories']['items']

        offset = 0
        while offset < 100:
            categories = _get_categories(country='DE', locale='en', limit=20,
                                          offset=offset)
            matches = list(
                filter(lambda c: c['name'].lower() == mood.lower(), categories))

            if matches:
                return matches[0]

            offset += 20
        return None


    def get_playlists_for_category(self, category_id):
        endpoint = self.api_base+f'/browse/categories/{category_id}/playlists'
        res = requests.get(endpoint,
                headers=self.get_headers()
            )
        if res.status_code != 200:
            raise Exception("Failed to fetch category playlists: " + res.reason)
        playlists = res.json()['playlists']['items']
        return list(map(Playlist.from_spotify, playlists))


@Singleton
class MusicService:
    def __init__(self, remote=None):
        if remote:
            self.remote = remote
        else:
            self.remote = SpotifyRemote.instance()

    def set_remote(self, remote: MusicRemote):
        self.remote = remote

    def get_playlist_for_mood(self, mood: str):

        with concurrent.futures.ThreadPoolExecutor() as executor:
            cat_future = executor.submit(self.remote.get_category_for_mood, mood=mood)
            up_future = executor.submit(self.remote.get_user_playlists)

            cat_match = cat_future.result()
            user_playlists = up_future.result()

        if cat_match:
            cat_playlists = self.remote.get_playlists_for_category(cat_match['id'])

            shared_playlists = set(user_playlists).intersection(set(cat_playlists))

            if shared_playlists:
                playlist = random.choice(list(shared_playlists))
            else:
                playlist = random.choice(cat_playlists)

        else:
            if user_playlists:
                playlist = random.choice(user_playlists)

        if not playlist:
            raise Exception("Couldn't find any matching playlist")

        return playlist

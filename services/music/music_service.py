from abc import ABC, abstractmethod
from os import environ
from dotenv import load_dotenv
import random
import concurrent.futures
import requests
import base64
from datetime import datetime as dt, timedelta
from urllib.parse import urlencode

from util import Singleton
from services.preferences import PrefService

class MusicRemote(ABC):
    @abstractmethod
    def get_playlist_for_mood(self, mood:str):
        pass

@Singleton
class SpotifyRemote(MusicRemote):
        def __init__(self):
            load_dotenv()

            required_env = (
                'spotify_client_id',
                'spotify_client_secret',
                'spotify_username'
            )

            self.pref_service = PrefService()
            pref = self.pref_service.get_preferences('music')
            if not all([var in pref for var in required_env]):
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

            client_id = self.pref_service.get_preferences('music').get('spotify_client_id')
            client_secret = self.pref_service.get_preferences('music').get('spotify_client_secret')
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

        def get_user_playlists(self, limit=20, offset=0):
            username = self.pref_service.get_preferences('music').get('spotify_username')
            endpoint=self.api_base+'/users/{username}/playlists'
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

        def get_categories(self, country, locale='en', limit=20, offset=0):
            endpoint=self.api_base+'/browse/categories'
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
            return res.json()

        def get_category_playlists(self, category_id):
            endpoint=self.api_base+f'/browse/categories/{category_id}/playlists'
            res = requests.get(endpoint,
                    headers=self.get_headers()
                )
            if res.status_code != 200:
                raise Exception("Failed to fetch category playlists: " + res.reason)
            return res.json()


        def get_playlist_for_mood(self, mood:str):
            def _request_user_playlists():
                offset = 0
                playlists = []
                while offset < 150:
                    answer = self.get_user_playlists(limit=50, offset=offset)
                    playlists.extend(answer['items'])
                    if int(answer['total']) < 50:
                        return playlists
                    offset += 50

            def _request_categories(offset):
                return self.get_categories(country='DE', locale='en', limit=20,
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
                cat_playlists = self.get_category_playlists(cat_match['id'])
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

            breakpoint()
            return playlist['external_urls']['spotify']

@Singleton
class MusicService:
    def __init__(self, remote=SpotifyRemote.instance()):
        self.remote = remote

    def set_remote(self, remote:MusicRemote):
        self.remote = remote

    def get_playlist_for_mood(self, mood:str):
        return self.remote.get_playlist_for_mood(mood)


import json
import time
from requests import *
from typing import Dict

token_info_typing = Dict[str, str | int]


def is_token_expired(token_info: token_info_typing) -> bool:
    now = int(time.time())
    return token_info['expires_at'] - now < 60


class SpotifyTokenCache:
    def __init__(self, client_id: str, client_secret: str, cache_file: str = 'token_cache.json') -> None:
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.cache_file = cache_file
        self.token_info: token_info_typing = self.load_token()

    def load_token(self):
        try:
            with open(self.cache_file, 'r') as file:
                token_info = json.load(file)
            if is_token_expired(token_info):
                return self.request_new_token()
            return token_info
        except FileNotFoundError:
            return self.request_new_token()

    def save_token(self, token_info: token_info_typing):
        with open(self.cache_file, 'w') as file:
            json.dump(token_info, file)

    def get_token(self):
        if is_token_expired(self.token_info):
            self.token_info = self.request_new_token()
        return self.token_info['access_token']

    def request_new_token(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        token_info: token_info_typing = post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=body
        ).json()

        token_info['expires_at'] = int(time.time()) + token_info.get('expires_in')
        self.save_token(token_info)

        return token_info

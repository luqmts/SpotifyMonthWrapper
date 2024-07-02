import json
import time
from os import getenv
from requests import post
from typing import Dict
import urllib.parse
from http.server import HTTPServer
from modules.SpotifyAuthHandler import SpotifyAuthHandler
from base64 import b64encode
from dotenv import load_dotenv

load_dotenv()
token_info_typing = Dict[str, str | int]


def is_token_expired(token_info: token_info_typing) -> bool:
    now = int(time.time())
    return token_info['expires_at'] - now < 60


class SpotifyTokenCache:

    auth_url: str = getenv('AUTH_URL')
    redirect_uri: str = getenv('REDIRECT_URI')

    def __init__(
            self: object,
            client_id: str,
            client_secret: str,
            scope: str,
            cache_file: str = 'token_cache.json'
    ) -> None:
        self.__client_id: str = client_id
        self.__client_secret: str = client_secret
        self.__scope: str = scope
        self.__cache_file: str = cache_file
        self.token_info: token_info_typing = self.load_token()
        self.__authorization_code: str = ''

    @property
    def client_id(self: object) -> str:
        return self.__client_id

    @property
    def client_secret(self: object) -> str:
        return self.__client_secret

    @property
    def scope(self: object) -> str:
        return self.__scope

    @property
    def authorization_code(self: object) -> str:
        return self.__authorization_code

    def load_token(self: object) -> None:
        try:
            with open(self.__cache_file, 'r') as file:
                token_info = json.load(file)
                self.__authorization_code = token_info.get('access_token')
            if is_token_expired(token_info):
                self.__authorization_code = self.get_authorization_code()
                return self.request_new_token()
            return token_info
        except FileNotFoundError:
            self.__authorization_code = self.get_authorization_code()
            return self.request_new_token()

    def save_token(self: object, token_info: token_info_typing) -> None:
        with open(self.__cache_file, 'w') as file:
            json.dump(token_info, file)

    def get_token(self: object) -> str:
        if is_token_expired(self.__token_info):
            self.__token_info = self.request_new_token()
        return self.__token_info['access_token']

    def get_authorization_code(self: object) -> str:
        auth_url: str = f"{SpotifyTokenCache.auth_url}?response_type=code&client_id={self.client_id}&scope={urllib.parse.quote(self.scope)}&redirect_uri={urllib.parse.quote(SpotifyTokenCache.redirect_uri)}"
        print(f"Vá para a seguinte URL e autorize o aplicativo para gerar o report mensal: \n{auth_url}")

        server_address = ('', 8888)
        httpd = HTTPServer(server_address, SpotifyAuthHandler)
        httpd.handle_request()
        return httpd.authorization_code

    def request_new_token(self: object) -> token_info_typing:
        auth_header = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }
        data = {
            'grant_type': 'authorization_code',
            "code": self.__authorization_code,
            "redirect_uri": SpotifyTokenCache.redirect_uri
        }

        token_info: token_info_typing = post(
            'https://accounts.spotify.com/api/token',
            headers=headers,
            data=data
        ).json()

        token_info['expires_at'] = int(time.time()) + token_info.get('expires_in')
        self.save_token(token_info)

        return token_info

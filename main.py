from modules.SpotifyTokenCache import SpotifyTokenCache
import os
from dotenv import load_dotenv
from requests import get

load_dotenv()

tokencache = SpotifyTokenCache(
    os.getenv('SPOTIPY_CLIENT_ID'),
    os.getenv('SPOTIPY_CLIENT_SECRET'),
    'user-top-read'
)


def get_top_tracks(bearer_token: str):
    response = get(
        'https://api.spotify.com/v1/me/top/tracks?time_range=short_term',
        headers=({'Authorization': f'Bearer {bearer_token}'})
    )

    return response.json().get('items')


if __name__ == '__main__':
    songs = get_top_tracks(tokencache.token_info.get('access_token'))

    for song in songs:
        print(f'Artista: {song.get('artists')[0].get('name')} - Música: {song.get('name')}')

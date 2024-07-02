from modules.SpotifyTokenCache import SpotifyTokenCache
import os
from dotenv import load_dotenv
from requests import get
from typing import List, Dict

load_dotenv()

tokencache: SpotifyTokenCache = SpotifyTokenCache(
    os.getenv('SPOTIPY_CLIENT_ID'),
    os.getenv('SPOTIPY_CLIENT_SECRET'),
    'user-top-read'
)


def get_top_tracks(bearer_token: str, top: int = 5) -> List:
    response = get(
        'https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5',
        headers=({'Authorization': f'Bearer {bearer_token}'})
    )

    return response.json().get('items')[0:top]


def get_top_artists(bearer_token: str) -> List:
    response = get(
        'https://api.spotify.com/v1/me/top/artists?time_range=short_term&limit=50',
        headers=({'Authorization': f'Bearer {bearer_token}'})
    )

    return response.json().get('items')


def get_top_genres(most_listened_artists: List, top: int = 5) -> List:
    dict_genres: Dict[str, int] = {}

    for artist in most_listened_artists:
        for genre in artist.get('genres'):
            if dict_genres.get(genre):
                dict_genres[genre] = dict_genres.get(genre) + 1
            else:
                dict_genres[genre] = 1

    dict_genres = dict(sorted(dict_genres.items(), key=lambda item: item[1], reverse=True))
    return list(dict_genres.items())[0:top]


if __name__ == '__main__':
    tracks: List = get_top_tracks(tokencache.token_info.get('access_token'), 5)
    artists: List = get_top_artists(tokencache.token_info.get('access_token'))
    genres: List = get_top_genres(artists, 5)

    print('Your top genres (last 4 weeks):'.center(50, '-'))
    for key, value in genres:
        print(f'{key}: {value}')

    print('-' * 50)
    print('Your top artists (last 4 weeks):'.center(50, '-'))
    for value in artists[0:5]:
        print(value.get('name'))

    print('-' * 50)
    print('Your top tracks (last 4 weeks):'.center(50, '-'))
    for value in tracks:
        print(f'{value.get('name')} (Artist: {value.get('artists')[0].get('name')})')

from typing import Optional, Tuple, List
from spotify_objects import Playlist, Song, create_default_playlist_name
from requests import Response, get, post, put


## TODO: have not been tested, run these api methods
def get_user_playlists_api(access_token: str, user_id: str) -> Tuple[
    Optional[List[Playlist]], 
    bool
]:
    response : Response = get(
        f'https://api.spotify.com/v1/users/{user_id}/playlists',
        access_token
    )
    if response.status_code != 200:
        print(f"Spotify API failed with status code {response.status_code}")
        return (None, False)

    playlists_found: List[Playlist] = []

    return (playlists_found, True)


def create_playlist_api(access_token: str, user_id: str) -> Tuple[Optional[Playlist], bool]:

    response : Response = post(
        f'https://api.spotify.com/v1/users/{user_id}/playlists',
        access_token
    )

    if response.status_code != 200:
        return (None, False)

    created_playlist: Playlist = Playlist(create_default_playlist_name())

    return (created_playlist, True)

def add_songs_to_playlist_api(
    access_token: str, 
    playlist_id: str, 
    song_ids: List[str]
) -> bool:

    response : Response = put(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        access_token
    )
    if response.status_code != 200:
        print(f"Spotify API failed with status code {response.status_code}")
        return False

    return True


def get_tracks_api(access_token: str) -> Tuple[Optional[List[Song]], bool]:
    response : Response = get(
        f'https://api.spotify.com/v1/tracks',
        access_token
    )
    if response.status_code != 200:
        print(f"Spotify API failed with status code {response.status_code}")
        return (None, False)

    songs_found: List[Song] = []

    return (songs_found, True)


class SpotifyClient:
    def create_playlist(self) -> Optional[Playlist]:
        return None

    def add_song(self, user_id: str, playlist_id: str, song: Song) -> Optional[bool]:
        return False

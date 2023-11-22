from typing import Optional, List, Dict, Any
from api_methods.spotify_objects import Playlist, Song 
from requests import Response, get, post, put
from helper_methods import (
    print_spotify_api_error, 
    create_default_playlist_name, 
    create_default_playlist_desc
)
from spotipy.oauth2 import SpotifyOAuth # type: ignore


def get_user_id_api(
    access_token: str,
) -> Optional[Response]:
    response : Response = get(
        url=f'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code != 200:
        print_spotify_api_error(response.status_code)
        return None
    
    return response

def get_user_playlists_api(
    access_token: str, 
    user_id: str
) -> Optional[Response]:
    response : Response = get(
        url=f'https://api.spotify.com/v1/users/{user_id}/playlists',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code != 200:
        print_spotify_api_error(response.status_code)
        return None
    
    return response


# TODO: [SP-51] use to update tracks
def get_playlist_tracks_api(
    access_token: str,
    playlist_id: str
) -> Optional[Response]:
    response : Response = get(
        url=f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code != 200:
        print_spotify_api_error(response.status_code)
        return None
    
    return response

def create_playlist_api(
    access_token: str, 
    user_id: str, 
    name: str,
    description: str,
    is_public: bool = True
) -> Optional[Response]:

    response : Response = post(
        url=f'https://api.spotify.com/v1/users/{user_id}/playlists',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        json={
            "name": name,
            "description": description,
            "public": "true" if is_public is True else "false"
        }
    )

    if response.status_code != 201:
        print_spotify_api_error(response.status_code)
        return None

    return response

def add_songs_to_playlist_api(
    access_token: str, 
    playlist_id: str, 
    song_uris: List[str]
) -> bool:
    response : Response = put(
        url=f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
        headers={
            'Authorization': f'Bearer {access_token}', 
            'Content-Type': 'application/json'
        },
        json={
            "uris": song_uris
        }
    )
    if response.status_code != 201:
        print_spotify_api_error(response.status_code)
        return False

    return True

def search_track_api(
    access_token: str, 
    name: str, 
    artist: str
) -> Optional[Response]:
    response: Response = get(
        url='https://api.spotify.com/v1/search',
        headers={
            'Authorization': f'Bearer {access_token}', 
            'Content-Type': 'application/json'
        },
        params={
            'q': f'{artist}: {name}',
            'type': 'track',
            'limit': '1'
        }
    )
    if response.status_code != 200:
        print_spotify_api_error(response.status_code)
        return None

    return response
    


class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.__access_token = None
        self.__set_new_access_token()
        self.__user_id = self.get_user_id()
        if self.__user_id is None:
            return None

    def __set_new_access_token(
        self
    )-> None:
        sp_oauth = SpotifyOAuth(
            self.__client_id,
            self.__client_secret,
            self.redirect_uri,
            scope=[
                'playlist-read-private',
                'playlist-read-collaborative',
                'playlist-modify-private',
                'playlist-modify-public',
            ]
        )
        ## TODO: [SP-54] fix later
        auth_url = sp_oauth.get_authorize_url()
        print(f'Please go to the url: {auth_url}')

        token = sp_oauth.get_access_token(
            code=None, check_cache=True
        )
        self.__access_token = token.get("access_token")

    def get_user_id(self) -> Optional[str]:
        response = get_user_id_api(
            access_token=self.__access_token
        )
        if response is None:
            return None
        
        json : Dict[str, Any] = response.json()
        id = json.get("id")
        if id is None:
            return None
        return id
    
    def get_user_playlists(self) -> Optional[List[Playlist]]:
        response = get_user_playlists_api(
            access_token=self.__access_token, user_id=self.__user_id
        )
        if response is None:
            return None

        json : Dict[str, Any] = response.json()
        items = json.get("items")
        if items is None:
            print("No playlists found.")
            return None

        return [ 
            Playlist(
                id=item['id'],
                playlist_name=item['name'],
                uri=item["uri"]
            ) for item in items
        ]
    
    def search_track(self, name: str, artist: str) -> Optional[Song]:
        response = search_track_api(
            access_token=self.__access_token, 
            name=name, 
            artist=artist
        )
        if response is None:
            print(f"Failed to get track '{name}' from artist '{artist}'.")
            return None
        
        tracks_found: Dict[str, Any] = response.json().get('tracks')
        if tracks_found is None:
            return None
        items = tracks_found.get("items")
        if items is None:
            return None

        return Song(
            id=items[0]['id'],
            name=items[0]['name'],
            uri=items[0]['uri'],
        )

    # method will create an empty playlist
    def create_playlist(
        self, 
        name=None, 
        description=None
    ) -> Optional[Playlist]:
        
        response = create_playlist_api(
            access_token=self.__access_token, 
            user_id=self.__user_id, 
            name=name if name else create_default_playlist_name(), 
            description=description if description else create_default_playlist_desc(),
        )
        if response is None:
            return None
        
        json_response = response.json()
        return Playlist(
            id=json_response["id"],
            playlist_name=json_response["name"],
            uri=json_response["uri"]
        )

    def add_songs(
        self, 
        playlist: Playlist, 
        songs: List[Song]
    ) -> bool:
        
        # adding 100 songs at a time
        while(len(songs) != 0):
            is_success = add_songs_to_playlist_api(
                access_token=self.__access_token,
                playlist_id=playlist.id,
                song_uris=[song.uri for song in songs[:100]]
            )

            if is_success is False:
                print("Failed to insert some songs. Please try again.")
                return False
            
            songs = songs[100:]

        return True
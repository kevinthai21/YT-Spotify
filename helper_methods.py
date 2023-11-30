import datetime
from enum import Flag

class PlaylistType(Flag):
    YOUTUBE = 'YOUTUBE'
    SPOTIFY = 'SPOTIFY'

def print_spotify_api_error(status_code):
    print(f"Spotify API failed with the status code {status_code}")

def create_default_playlist_name() -> str:
    now = datetime.datetime.now()
    return f"Transferred Playlist {now.month}-{now.day}-{now.year} {now.hour}:{now.minute}"

def create_default_playlist_desc() -> str:
    return """Playlist created with a program by @kevin.thai21
To learn more, look for kevinthai21/YT-Spotify on Github!
"""

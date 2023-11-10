from typing import List
import datetime

class Song:
    name: str
    artist: str
    uri: str

class Playlist:
    def __init__(self, playlist_name, uri = ""):
        self.name = playlist_name # str
        self.songs = [] # List[Song]
        self.uri = uri

    def size(self) -> int:
        return len(self.songs)
    

def create_default_playlist_name() -> str:
    now = datetime.datetime.now()
    return f"Playlist {now.year}.{now.month}.{now.day} {now.hour}:{now.minute}" 

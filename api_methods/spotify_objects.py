from typing import List
from base_music import BaseSong, BasePlaylist

class SpotifySong(BaseSong):
    def __init__(self, id, name, uri): 
        super().__init__(self, id, name)
        self.uri = uri

class SpotifyPlaylist(BasePlaylist):
    def __init__(self, id, name, uri=""):
        super().__init__(self,id, name)
        self.songs: List[SpotifySong] = []
        self.uri = uri
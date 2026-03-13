from typing import List
from base_music import BaseSong, BasePlaylist


class SpotifySong(BaseSong):
    def __init__(self, id: str, name: str, uri: str):
        super().__init__(id=id, name=name, uri=uri)  # removed erroneous extra `self`


class SpotifyPlaylist(BasePlaylist):
    def __init__(self, id: str, name: str, uri: str = ""):
        super().__init__(id=id, name=name, uri=uri)  # removed erroneous extra `self`
        self.songs: List[SpotifySong] = []

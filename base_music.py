from typing import List, Optional


class BaseSong:
    def __init__(self, id: str = "", name: str = "", uri: str = ""):
        self.id: str = id
        self.name: str = name
        self.uri: str = uri
        self.artist: str = ""  # populated when fetching Spotify playlist tracks


class BasePlaylist:
    def __init__(self, id: str = "", name: str = "", uri: str = ""):
        self.id: str = id
        self.name: str = name
        self.uri: str = uri
        self.songs: List[BaseSong] = []

    def size(self) -> int:
        return len(self.songs)
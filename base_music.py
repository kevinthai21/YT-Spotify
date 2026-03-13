from typing import List, Optional


class BaseSong:
    def __init__(self, id: str = "", name: str = "", uri: str = ""):
        self.id: str = id
        self.name: str = name
        self.uri: str = uri  # needed by both Spotify (spotify:track:xxx) and YouTube


class BasePlaylist:
    def __init__(self, id: str = "", name: str = "", uri: str = ""):
        self.id: str = id
        self.name: str = name
        self.uri: str = uri
        self.songs: List[BaseSong] = []

    def size(self) -> int:
        return len(self.songs)

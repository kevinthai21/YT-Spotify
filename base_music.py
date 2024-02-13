from typing import List

class BaseSong:
    def __init__(self, id: str = "", name: str= ""):
        self.id: str = id
        self.name: str = name

class BasePlaylist:
    def __init__(self, id="", name=""):
        self.id: str = id
        self.name: str = name
        self.songs: List[BaseSong] = []
    
    def size(self):
        return len(self.songs)
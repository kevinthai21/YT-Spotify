from typing import List
from base_music import BaseSong, BasePlaylist


class YouTubeVideo(BaseSong):
    def __init__(self, id: str, name: str, channel: str):
        super().__init__(id=id, name=name)  # removed erroneous extra `self`
        self.channel: str = channel


class YouTubePlaylist(BasePlaylist):
    def __init__(self, id: str, name: str, description: str = ""):
        super().__init__(id=id, name=name)  # removed erroneous extra `self`
        self.songs: List[YouTubeVideo] = []
        self.description: str = description

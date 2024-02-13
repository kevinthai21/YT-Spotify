from typing import List
from base_music import BaseSong, BasePlaylist

class YouTubeVideo(BaseSong):
	def __init__(self, name, channel):
		super().__init__(self, name)
		self.channel = channel


class YouTubePlaylist(BasePlaylist):
	def __init__(self):
		super().__init__(self) 
		self.songs: List[YouTubeVideo] = []


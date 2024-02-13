from typing import List
from base_music import BaseSong, BasePlaylist

class YouTubeVideo(BaseSong):
	def __init__(self, id, name, channel):
		super().__init__(self, id, name)
		self.channel = channel


class YouTubePlaylist(BasePlaylist):
	def __init__(self, id, name, description):
		super().__init__(self, id, name) 
		self.songs: List[YouTubeVideo] = []
		self.description = description


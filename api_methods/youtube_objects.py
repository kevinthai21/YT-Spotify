from typing import List

class YouTubeVideo:
	name: str
	channel: str

class YouTubePlaylist:

	def __init__(self):
		self.id = ""
		self.videos = [] # List[YouTubeVideo] 

	def size(self):
		return len(self.videos)


from typing import Tuple, Optional, List
from youtube_objects import YouTubeVideo, YouTubePlaylist

class YouTubeAPI:

    def read_playlist(self, playlist_link: str) -> Tuple[
        Optional[YouTubePlaylist], 
        bool
    ]:
        # add implementation here
        playlist = None
        return (playlist, True)

    
class YouTubeClient:

    def __init__(self):
        ...
    
    def create_playlist(self) -> Optional[YouTubePlaylist]:
        pass
    
    def search_video(self, search_term: str) -> Optional[YouTubeVideo]:
        pass
    
    def add_videos_to_playlist(
        self, playlist: YouTubePlaylist, videos: List[YouTubeVideo]
    ):
        pass

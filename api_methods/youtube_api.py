from typing import Tuple, Optional
from youtube_objects import YouTubeVideo, YouTubePlaylist

class YouTubeAPI:

    def read_playlist(self, playlist_link: str) -> Tuple[
        Optional[YouTubePlaylist], 
        bool
    ]:
        # add implementation here
        playlist = None
        return (playlist, True)

    
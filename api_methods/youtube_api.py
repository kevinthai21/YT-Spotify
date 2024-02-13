from typing import Optional, List
from youtube_objects import YouTubeVideo, YouTubePlaylist
from requests import Response, get, post, put
from helper_methods import print_youtube_api_error, create_default_playlist_desc, create_default_playlist_name
from time import sleep

class YouTubeAPI:
    def __init__(self, access_key: str, access_token: str):
        self.__access_key = access_key
        self.__access_token = access_token

    def get_user_playlists(self, page_token: Optional[str] = None) -> Optional[Response]:
        response: Response = get(
            url=f'https://youtube.googleapis.com/youtube/v3/playlists?part=snippet%2CcontentDetails&maxResults=50&mine=true&key={self.__access_key}' if page_token is None else f'https://youtube.googleapis.com/youtube/v3/playlists?part=snippet%2CcontentDetails&pageToken={page_token}&maxResults=50&mine=true&key={self.__access_key}',
            headers= {
                'Authorization:': f'Bearer {self.__access_token}',
                'Accept:': 'application/json',
            }
        )
        if response.status_code != 200:
            print_youtube_api_error(response.status_code)
            return None
        return response

    def get_playlist_videos(self, playlist_id: str, page_token: Optional[str] = None) -> Optional[Response]:
        response: Response = get(
            url=f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={playlist_id}&key={self.__access_key}' if page_token is None else f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&pageToken={page_token}&maxResults=50&playlistId={playlist_id}&key={self.__access_key}',
            headers= {
                'Authorization:': f'Bearer {self.__access_token}',
                'Accept:': 'application/json',
            }
        )
        if response.status_code != 200:
            print_youtube_api_error(response.status_code)
            return None
        return response
        
    def create_playlist(self, playlist_name: str, playlist_description: str) -> Optional[Response]:
        response: Response = post(
            url=f'https://youtube.googleapis.com/youtube/v3/playlists?part=snippet%2Cstatus&key={self.__access_key}', 
            headers={
                'Authorization:': f'Bearer {self.__access_token}',
                'Accept:': 'application/json',
                'Content-Type:': 'application/json',
            },
            data={
                'snippet': {
                    "title": playlist_name,
                    "description": playlist_description,
                    "status": {
                        "privacyStatus": "private"
                    }                    
                }
            }
        )
        if response != 200:
            print_youtube_api_error(response.status_code)
            return None
    
    # return number of videos successfully inserted
    def add_videos_to_playlist(self, playlist_id: str, video_ids: List[str]) -> int:
        num_inserted: int = 0
        for video_id in video_ids:
            response: Response = put(
                url=f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet&key={self.__access_key}',
                headers= {
                    'Authorization:': f'Bearer {self.__access_token}',
                    'Accept:': 'application/json'
                },
                data={
                    'snippet': {
                        'playlistId': {playlist_id},
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': {video_id}
                        }
                    }
                }
            )
            if response.status_code != 200:
                print_youtube_api_error(response.status_code)
                print(f"Unable to insert video id: {video_id}")
            num_inserted += 1
            sleep(10) # cooldown
        return num_inserted

    def search_video(self, search_query: str) -> Optional[Response]:
        response: Response = get(
            url=f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={search_query}&key={self.__access_key}",
            headers= {
                'Authorization:': f'Bearer {self.__access_token}',
                'Accept:': 'application/json'
            }
        )
        if response.status_code != 200:
            print_youtube_api_error(response.status_code)
            return None    
    
class YouTubeClient:

    def __init__(self):
        self._youtube_api = YouTubeAPI(access_key="", access_token="")
    
    def get_user_playlists(self) -> Optional[List[YouTubePlaylist]]:
        is_start: bool = True
        next_page_token: Optional[str] = None
        youtube_playlists = []
        while(is_start or next_page_token is not None):
            response = self._youtube_api.get_user_playlists(page_token=next_page_token)
            if response is None:
                return None
            response_json = response.json()
            for item in response_json['items']:
                youtube_playlists.append(
                    YouTubePlaylist(
                        id=item['id'], name=item['snippet']['title'], description=item['snippet']['description']
                    )
                )
            next_page_token = response_json.get('nextPageToken')
            if is_start == True:
                is_start = False
        return youtube_playlists


    def get_playlist_videos(self, playlist: YouTubePlaylist) -> Optional[List[YouTubeVideo]]:
        is_start: bool = True
        next_page_token: Optional[str] = None
        while (is_start or next_page_token is not None): # if ever less than 50, then no need to query more
            response = self._youtube_api.get_playlist_videos(
                playlist_id=playlist.id, page_token=next_page_token
            )
            if response is None:
                return None
            response_json = response.json()
            next_page_token = response_json.get('nextPageToken')
            youtube_videos: List[YouTubeVideo] = []
            for item in response["items"]:
                video = YouTubeVideo(
                    id=item['snippet']['resourceId']['videoId'], 
                    name=item['snippet']['title'],
                    channel=item['snippet']['channelId']
                )
                youtube_videos.append(video)
            if is_start == True:
                is_start = False
        return youtube_videos
        
    
    def create_playlist(self, playlist_name: Optional[str]=None, playlist_description: Optional[str] = None) -> Optional[YouTubePlaylist]:
        playlist_name = playlist_name if playlist_name else create_default_playlist_name()
        response = self._youtube_api.create_playlist(
            playlist_name=playlist_name,
            playlist_description= playlist_description if playlist_description else create_default_playlist_desc()
        )
        if response is None:
            return None
        playlist_id = response['id']
        return YouTubePlaylist(playlist_id, playlist_name)
    
    def search_video(self, name: str, artist: str) -> Optional[YouTubeVideo]:
        response = self._youtube_api.search_video(f"{artist} - {name}")
        if response is None:
            return None
        youtubeVideoId = response["items"][0]["id"]["videoId"]
        channelId = response["items"][0]["snippet"]["channelId"]
        videoTitle = response["items"][0]["snippet"]["title"]
        return YouTubeVideo(
            id=youtubeVideoId, name=videoTitle, channel=channelId
        )
    
    def add_videos_to_playlist(
        self, playlist: YouTubePlaylist, videos: List[YouTubeVideo]
    ) -> None:
        num_inserted = self._youtube_api.add_videos_to_playlist(
            playlist_id=playlist.id,video_ids=[video.id for video in videos]
        )
        if len(videos) != num_inserted:
            print(f"Found {len(videos)} videos, but only to insert {num_inserted} videos.")
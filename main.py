from helper_methods import PlaylistType
from api_methods.youtube_objects import YouTubePlaylist, YouTubeVideo
from api_methods.spotify_api import SpotifyClient
from api_methods.youtube_api import YouTubeAPI, YouTubeClient
from typing import Optional, List
from api_methods.spotify_objects import (
    Playlist as SpotifyPlaylist, 
    Song as SpotifySong
)

def create_spotify_playlist_from_youtube_playlist(
    spotify_client: SpotifyClient,
    youtube_playlist: YouTubePlaylist,
    playlist_name: Optional[str] = None,
    description_name: Optional[str] = None
) -> Optional[SpotifyPlaylist]:
    
    valid_songs_to_add: List[SpotifySong] = []
    for video in youtube_playlist.videos:
        song_found = spotify_client.search_track(
            name=video.name, artist=video.channel
        )
        if song_found is None:
            print(f'Could not find song: {video.name} - {video.channel}')
            continue
        valid_songs_to_add.append(song_found)

    # if no songs found, don't do anything    
    if valid_songs_to_add == 0:
        print("No valid songs found.")
        return None
    
    # if a song found, create a playlist
    created_playlist = spotify_client.create_playlist(
        name=playlist_name,
        description=description_name
    )

    if created_playlist is None:
        return None
    
    spotify_client.add_songs(
        playlist=created_playlist, songs=valid_songs_to_add
    )

    return created_playlist
    

def create_youtube_playlist_from_spotify_playlist(
    youtube_client: YouTubeClient,
    spotify_playlist: SpotifyPlaylist
):
    
    valid_videos: List[YouTubeVideo] = []
    for song in spotify_playlist.songs:
        video_found = youtube_client.search_video(
            search_term=f'{song.name}'
        )
        if video_found is None:
            print(f'Could not find song: {song.name}')
            continue
        valid_videos.append(video_found)

    # if no songs found, don't do anything    
    if valid_videos == 0:
        print("No valid songs found.")
        return None
    
    # if a song found, create a playlist
    created_playlist = youtube_client.create_playlist()

    if created_playlist is None:
        return None
    
    youtube_client.add_videos_to_playlist(
        playlist=created_playlist, videos=valid_videos
    )

    return created_playlist
    

def create_playlist(playlist_type: PlaylistType):
    spotify_client = SpotifyClient()
    youtube_client = YouTubeClient()

    if playlist_type == PlaylistType.SPOTIFY:
        playlist, is_success = youtube_client.read_playlist()
        if is_success is False or playlist is None:
            return -1
        create_spotify_playlist_from_youtube_playlist(
            spotify_client, playlist
        )
    elif playlist_type == PlaylistType.YOUTUBE:
        ## TODO: fix this once we are done with youtube api
        playlist = spotify_client.get_user_playlists()
        create_youtube_playlist_from_spotify_playlist(
            youtube_client, playlist[0]
        )
    else:
        return
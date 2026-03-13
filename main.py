import os
from typing import Optional, List
from dotenv import load_dotenv

from helper_methods import PlaylistType
from api_methods.youtube_objects import YouTubePlaylist, YouTubeVideo
from api_methods.spotify_api import SpotifyClient
from api_methods.youtube_api import YouTubeClient
from api_methods.spotify_objects import SpotifyPlaylist, SpotifySong
from base_music import BaseSong, BasePlaylist

load_dotenv()


# ── YouTube → Spotify ──────────────────────────────────────────────────────────

def create_spotify_playlist_from_youtube_playlist(
    spotify_client: SpotifyClient,
    youtube_playlist: YouTubePlaylist,
    playlist_name: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[BasePlaylist]:

    print(f"\nSearching Spotify for {len(youtube_playlist.songs)} video(s)...\n")

    matched: List[BaseSong] = []
    missed: List[YouTubeVideo] = []

    for video in youtube_playlist.songs:
        song = spotify_client.search_track(name=video.name, artist=video.channel)
        if song is None:
            missed.append(video)
        else:
            matched.append(song)

    # Report misses
    if missed:
        print(f"\n  Could not find {len(missed)} song(s) on Spotify:")
        for v in missed:
            print(f"    - {v.name} [{v.channel}]")

    # Nothing matched at all — bail out
    if not matched:  # fixed: was `== 0` which compares list to int (always False)
        print("\nNo songs matched on Spotify. Playlist not created.")
        return None

    print(f"\n  Matched {len(matched)}/{len(youtube_playlist.songs)} song(s).")

    # Create the playlist and populate it
    created = spotify_client.create_playlist(name=playlist_name, description=description)
    if created is None:
        print("ERROR: Failed to create Spotify playlist.")
        return None

    print(f"\nCreated Spotify playlist: '{created.name}'")
    success = spotify_client.add_songs(playlist=created, songs=matched)
    if not success:
        print("ERROR: Some songs could not be added.")

    return created


# ── Spotify → YouTube ──────────────────────────────────────────────────────────

def create_youtube_playlist_from_spotify_playlist(
    youtube_client: YouTubeClient,
    spotify_playlist: BasePlaylist,
    playlist_name: Optional[str] = None,
) -> Optional[YouTubePlaylist]:

    print(f"\nSearching YouTube for {len(spotify_playlist.songs)} song(s)...\n")

    matched: List[YouTubeVideo] = []
    missed: List[BaseSong] = []

    for song in spotify_playlist.songs:
        video = youtube_client.search_video(name=song.name, artist="")
        if video is None:
            missed.append(song)
        else:
            matched.append(video)

    if missed:
        print(f"\n  Could not find {len(missed)} song(s) on YouTube:")
        for s in missed:
            print(f"    - {s.name}")

    if not matched:  # fixed: was `== 0`
        print("\nNo videos matched on YouTube. Playlist not created.")
        return None

    print(f"\n  Matched {len(matched)}/{len(spotify_playlist.songs)} song(s).")

    created = youtube_client.create_playlist(playlist_name=playlist_name)
    if created is None:
        print("ERROR: Failed to create YouTube playlist.")
        return None

    print(f"\nCreated YouTube playlist: '{created.name}'")
    youtube_client.add_videos_to_playlist(playlist=created, videos=matched)
    return created


# ── Entry point ────────────────────────────────────────────────────────────────

def create_playlist(playlist_type: PlaylistType) -> None:
    spotify_client = SpotifyClient(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),        # fixed: os.getenv not os.get_env
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    )
    youtube_client = YouTubeClient()

    if playlist_type == PlaylistType.SPOTIFY:
        # Pick a YouTube playlist interactively, fetch its videos, transfer to Spotify
        youtube_playlist = youtube_client.pick_playlist()
        if youtube_playlist is None:
            return

        youtube_playlist.songs = youtube_client.get_playlist_videos(youtube_playlist) or []
        if not youtube_playlist.songs:
            print("The selected playlist has no videos.")
            return

        create_spotify_playlist_from_youtube_playlist(spotify_client, youtube_playlist)

    elif playlist_type == PlaylistType.YOUTUBE:
        # Pick a Spotify playlist and transfer to YouTube
        user_playlists = spotify_client.get_user_playlists()
        if not user_playlists:
            print("No Spotify playlists found.")
            return

        print(f"\nFound {len(user_playlists)} Spotify playlist(s):\n")
        for i, pl in enumerate(user_playlists):
            print(f"  [{i + 1}] {pl.name}")

        raw = input("\nEnter the playlist number to transfer: ").strip()
        if not raw.isdigit() or not (1 <= int(raw) <= len(user_playlists)):
            print("Invalid selection.")
            return

        selected = user_playlists[int(raw) - 1]
        create_youtube_playlist_from_spotify_playlist(youtube_client, selected)

    else:
        print(f"Unknown playlist type: {playlist_type}")


if __name__ == "__main__":
    create_playlist(PlaylistType.SPOTIFY)

import os
from typing import Optional, List
from dotenv import load_dotenv

from helper_methods import PlaylistType
from api_methods.youtube_objects import YouTubePlaylist, YouTubeVideo
from api_methods.spotify_api import SpotifyClient
from api_methods.youtube_api import YouTubeClient
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

    if missed:
        print(f"\n  Could not find {len(missed)} song(s) on Spotify:")
        for v in missed:
            print(f"    - {v.name} [{v.channel}]")

    if not matched:
        print("\nNo songs matched on Spotify. Playlist not created.")
        return None

    print(f"\n  Matched {len(matched)}/{len(youtube_playlist.songs)} song(s).")

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
    spotify_client: SpotifyClient,
    spotify_playlist: BasePlaylist,
) -> Optional[YouTubePlaylist]:
    """
    Transfer a single Spotify playlist to YouTube.
    Fetches the full track list first, then searches YouTube for each song
    using 'Artist - Song Name' for a one-to-one match.
    """
    print(f"\n  Fetching tracks for '{spotify_playlist.name}'...")
    tracks = spotify_client.get_playlist_tracks(spotify_playlist)

    if not tracks:
        print(f"  Playlist '{spotify_playlist.name}' is empty — skipping.")
        return None

    print(f"  Searching YouTube for {len(tracks)} track(s)...\n")

    matched: List[YouTubeVideo] = []
    missed: List[BaseSong] = []

    for song in tracks:
        # Use the stored artist field for accurate one-to-one search
        video = youtube_client.search_video(name=song.name, artist=song.artist)
        if video is None:
            missed.append(song)
        else:
            matched.append(video)

    if missed:
        print(f"\n  Could not find {len(missed)} track(s) on YouTube:")
        for s in missed:
            print(f"    - {s.artist} - {s.name}")

    if not matched:
        print(f"\n  No videos matched for '{spotify_playlist.name}'. Playlist not created.")
        return None

    print(f"\n  Matched {len(matched)}/{len(tracks)} track(s).")

    created = youtube_client.create_playlist(playlist_name=spotify_playlist.name)
    if created is None:
        print("  ERROR: Failed to create YouTube playlist.")
        return None

    print(f"  Created YouTube playlist: '{created.name}'")
    youtube_client.add_videos_to_playlist(playlist=created, videos=matched)
    return created


# ── Selection helpers ──────────────────────────────────────────────────────────

def _print_spotify_playlists(playlists: List[BasePlaylist]) -> None:
    print(f"\nFound {len(playlists)} Spotify playlist(s):\n")
    for i, pl in enumerate(playlists):
        print(f"  [{i + 1:>3}] {pl.name}")
    print(f"  [  0] Transfer ALL playlists")


def _pick_spotify_playlists(playlists: List[BasePlaylist]) -> Optional[List[BasePlaylist]]:
    """
    Let the user pick one, several, a range, or all playlists.
    Accepts:
      - '0'        → all playlists
      - '1'        → single index
      - '1,3,5'    → comma-separated indexes
      - '2-4'      → inclusive range
    """
    _print_spotify_playlists(playlists)
    print("\nExamples:  0 (all)  |  3  |  1,4,6  |  2-5")
    raw = input("Selection: ").strip()

    if raw == "0":
        print("  Transferring ALL playlists.")
        return playlists

    selected: List[BasePlaylist] = []
    try:
        for part in raw.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                for idx in range(int(start), int(end) + 1):
                    selected.append(playlists[idx - 1])
            else:
                selected.append(playlists[int(part) - 1])
    except (ValueError, IndexError):
        print("  Invalid selection.")
        return None

    return selected


# ── Entry point ────────────────────────────────────────────────────────────────

def create_playlist(playlist_type: PlaylistType) -> None:
    spotify_client = SpotifyClient(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    )
    youtube_client = YouTubeClient()

    if playlist_type == PlaylistType.SPOTIFY:
        # YouTube → Spotify
        youtube_playlist = youtube_client.pick_playlist()
        if youtube_playlist is None:
            return

        youtube_playlist.songs = youtube_client.get_playlist_videos(youtube_playlist) or []
        if not youtube_playlist.songs:
            print("The selected playlist has no videos.")
            return

        create_spotify_playlist_from_youtube_playlist(spotify_client, youtube_playlist)

    elif playlist_type == PlaylistType.YOUTUBE:
        # Spotify → YouTube
        user_playlists = spotify_client.get_user_playlists()
        if not user_playlists:
            print("No Spotify playlists found.")
            return

        selected = _pick_spotify_playlists(user_playlists)
        if not selected:
            return

        print(f"\nTransferring {len(selected)} playlist(s) to YouTube...\n")
        succeeded = 0
        for i, playlist in enumerate(selected, start=1):
            print(f"{'='*60}")
            print(f"[{i}/{len(selected)}] {playlist.name}")
            print(f"{'='*60}")
            result = create_youtube_playlist_from_spotify_playlist(
                youtube_client, spotify_client, playlist
            )
            if result:
                succeeded += 1

        print(f"\nDone! Successfully transferred {succeeded}/{len(selected)} playlist(s) to YouTube.")

    else:
        print(f"Unknown playlist type: {playlist_type}")


if __name__ == "__main__":
    create_playlist(PlaylistType.YOUTUBE)
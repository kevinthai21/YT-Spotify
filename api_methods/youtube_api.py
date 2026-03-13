import os
import sys
from typing import Optional, List
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from api_methods.youtube_objects import YouTubeVideo, YouTubePlaylist
from helper_methods import (
    print_youtube_api_error,
    create_default_playlist_desc,
    create_default_playlist_name,
)

# ── OAuth config ───────────────────────────────────────────────────────────────

load_dotenv()

CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE")
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
# ──────────────────────────────────────────────────────────────────────────────


def get_authenticated_service():
    """
    Authenticate via OAuth 2.0 and return a YouTube API service object.
    - On first run: opens a browser window for you to log in and authorize.
    - On subsequent runs: reuses the cached token in token.json.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    print(CLIENT_SECRETS_FILE)
    print(TOKEN_FILE)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing YouTube access token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"ERROR: '{CLIENT_SECRETS_FILE}' not found.")
                print("Download your OAuth 2.0 credentials JSON from Google Cloud Console")
                print("and save it as 'client_secrets.json' next to this script.")
                sys.exit(1)
            print("Opening browser for YouTube OAuth authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print(f"YouTube token saved to {TOKEN_FILE}")

    return build("youtube", "v3", credentials=creds)


# ── YouTubeClient ──────────────────────────────────────────────────────────────

class YouTubeClient:
    """
    High-level YouTube client using the google-api-python-client library.
    Uses OAuth 2.0 so unlisted videos and playlists are accessible.
    """

    def __init__(self):
        self._youtube = get_authenticated_service()

    # ── Playlists ──────────────────────────────────────────────────────────────

    def get_user_playlists(self) -> Optional[List[YouTubePlaylist]]:
        """Return all playlists owned by the authenticated user."""
        playlists: List[YouTubePlaylist] = []
        next_page_token: Optional[str] = None

        while True:
            response = (
                self._youtube.playlists()
                .list(
                    part="snippet,contentDetails",
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token,
                )
                .execute()
            )

            for item in response.get("items", []):
                playlists.append(
                    YouTubePlaylist(
                        id=item["id"],
                        name=item["snippet"]["title"],
                        description=item["snippet"].get("description", ""),
                    )
                )

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return playlists

    def pick_playlist(self) -> Optional[YouTubePlaylist]:
        """
        Fetch user's playlists, print them, and let the user pick one
        interactively. Returns the selected YouTubePlaylist.
        """
        playlists = self.get_user_playlists()
        if not playlists:
            print("No playlists found on this account.")
            return None

        print(f"\nFound {len(playlists)} playlist(s):\n")
        for i, pl in enumerate(playlists):
            print(f"  [{i + 1}] {pl.name}  [ID: {pl.id}]")

        while True:
            raw = input("\nEnter the playlist number to transfer: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(playlists):
                return playlists[int(raw) - 1]
            print("  Invalid selection, please try again.")

    def get_playlist_videos(self, playlist: YouTubePlaylist) -> Optional[List[YouTubeVideo]]:
        """
        Fetch all videos in a playlist, including unlisted ones.
        Uses contentDetails to get videoId, then fetches snippet separately
        to get the channel title (not just channelId).
        """
        video_ids: List[str] = []
        next_page_token: Optional[str] = None

        # Step 1: collect all video IDs from playlistItems
        while True:
            response = (
                self._youtube.playlistItems()
                .list(
                    part="contentDetails",
                    playlistId=playlist.id,
                    maxResults=50,
                    pageToken=next_page_token,
                )
                .execute()
            )

            for item in response.get("items", []):
                video_ids.append(item["contentDetails"]["videoId"])

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        if not video_ids:
            return []

        # Step 2: fetch full snippet for all video IDs (batches of 50)
        videos: List[YouTubeVideo] = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i : i + 50]
            response = (
                self._youtube.videos()
                .list(part="snippet", id=",".join(batch))
                .execute()
            )
            for item in response.get("items", []):
                videos.append(
                    YouTubeVideo(
                        id=item["id"],
                        name=item["snippet"]["title"],
                        # channelTitle gives the human-readable name, not just ID
                        channel=item["snippet"]["channelTitle"],
                    )
                )

        return videos

    # ── Create & populate playlist ─────────────────────────────────────────────

    def create_playlist(
        self,
        playlist_name: Optional[str] = None,
        playlist_description: Optional[str] = None,
    ) -> Optional[YouTubePlaylist]:
        name = playlist_name or create_default_playlist_name()
        desc = playlist_description or create_default_playlist_desc()

        response = (
            self._youtube.playlists()
            .insert(
                part="snippet,status",
                body={
                    "snippet": {"title": name, "description": desc},
                    "status": {"privacyStatus": "private"},
                },
            )
            .execute()
        )

        if not response:
            print_youtube_api_error("no response")
            return None

        return YouTubePlaylist(
            id=response["id"],
            name=response["snippet"]["title"],
            description=response["snippet"].get("description", ""),
        )

    def add_videos_to_playlist(
        self, playlist: YouTubePlaylist, videos: List[YouTubeVideo]
    ) -> None:
        """Insert videos into a playlist one at a time (API requirement)."""
        num_inserted = 0
        for video in videos:
            try:
                self._youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist.id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video.id,
                            },
                        }
                    },
                ).execute()
                num_inserted += 1
            except Exception as e:
                print(f"  ERROR: Could not insert video '{video.name}': {e}")

        if num_inserted != len(videos):
            print(f"  WARNING: Inserted {num_inserted}/{len(videos)} videos.")
        else:
            print(f"  Successfully inserted all {num_inserted} video(s).")

    # ── Search ─────────────────────────────────────────────────────────────────

    def search_video(self, name: str, artist: str) -> Optional[YouTubeVideo]:
        """Search YouTube for a song and return the top result."""
        query = f"{artist} - {name}"
        response = (
            self._youtube.search()
            .list(part="snippet", q=query, maxResults=1, type="video")
            .execute()
        )

        items = response.get("items", [])
        if not items:
            print(f"  [MISS] No YouTube result for '{query}'.")
            return None

        item = items[0]
        return YouTubeVideo(
            id=item["id"]["videoId"],
            name=item["snippet"]["title"],
            channel=item["snippet"]["channelTitle"],
        )

import re
from typing import Optional, List, Dict, Any
from requests import Response, get, post
from helper_methods import (
    print_spotify_api_error,
    create_default_playlist_name,
    create_default_playlist_desc,
)
from base_music import BasePlaylist, BaseSong
from spotipy.oauth2 import SpotifyOAuth  # type: ignore


# ── Low-level API calls ────────────────────────────────────────────────────────

def get_user_id_api(access_token: str) -> Optional[Response]:
    response: Response = get(
        url="https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if response.status_code != 200:
        print_spotify_api_error(response.status_code)
        return None
    return response


def get_user_playlists_api(
    access_token: str, offset: int = 0, limit: int = 50
) -> Optional[Response]:
    response: Response = get(
        url="https://api.spotify.com/v1/me/playlists",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": limit, "offset": offset},
    )
    if response.status_code != 200:
        print_spotify_api_error(response.status_code)
        return None
    return response


def get_playlist_tracks_api(
    access_token: str, playlist_id: str, offset: int = 0
) -> Optional[Response]:
    response: Response = get(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"limit": 100, "offset": offset},
    )
    if response.status_code != 200:
        print_spotify_api_error(response.status_code)
        return None
    return response


def create_playlist_api(
    access_token: str,
    name: str,
    description: str,
    is_public: bool = False,
) -> Optional[Response]:
    response: Response = post(
        url="https://api.spotify.com/v1/me/playlists",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={
            "name": name,
            "description": description,
            "public": is_public,
        },
    )
    if response.status_code != 201:
        print_spotify_api_error(response.status_code)
        return None
    return response


def add_songs_to_playlist_api(
    access_token: str, playlist_id: str, song_uris: List[str]
) -> bool:
    response: Response = post(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json={"uris": song_uris},
    )
    if response.status_code != 201:
        print_spotify_api_error(response.status_code)
        return False
    return True


# ── Search helpers ─────────────────────────────────────────────────────────────

def _raw_search(access_token: str, query: str, limit: int = 5) -> List[Dict]:
    """Execute a single Spotify search and return track items (empty list on failure)."""
    response: Response = get(
        url="https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query, "type": "track", "limit": limit},
    )
    if response.status_code != 200:
        return []
    return response.json().get("tracks", {}).get("items", [])


def _clean_title(title: str) -> str:
    """
    Strip common YouTube noise so Spotify has a better chance of matching.
    e.g. "Blinding Lights (Official Video) [HD]" -> "Blinding Lights"
    """
    noise_patterns = [
        r"\(official\s*(music\s*)?video\)",
        r"\(official\s*audio\)",
        r"\(lyrics?\s*(video)?\)",
        r"\(audio\)",
        r"\(hd\)",
        r"\(4k\)",
        r"\(visualizer\)",
        r"\[.*?\]",
        r"\(.*?version\)",
        r"\(.*?remaster.*?\)",
        r"ft\..*",
        r"feat\..*",
        r"\|.*",
    ]
    result = title
    for pattern in noise_patterns:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE)
    return result.strip()


def _parse_artist_and_title(raw_title: str, channel: str):
    """
    Many YouTube music videos follow "Artist - Song Title".
    If that pattern is detected, split and return (artist, title).
    Otherwise fall back to (channel, cleaned_title).
    """
    # Match "Artist - Title" or "Artist – Title" (en-dash)
    match = re.match(r"^(.+?)\s[-\u2013]\s(.+)$", raw_title.strip())
    if match:
        return match.group(1).strip(), _clean_title(match.group(2).strip())
    return channel, _clean_title(raw_title)


def _pick_best_track(items: List[Dict], artist: str) -> Optional[Dict]:
    """
    Pick the best track from a result list.
    Prefers a result whose artist name matches, falls back to most popular.
    """
    if not items:
        return None
    artist_lower = artist.lower()
    for item in items:
        track_artists = [a["name"].lower() for a in item.get("artists", [])]
        if any(artist_lower in a or a in artist_lower for a in track_artists):
            return item
    return max(items, key=lambda t: t.get("popularity", 0))


def search_track_api(
    access_token: str, name: str, artist: str
) -> Optional[Dict]:
    """
    Try progressively looser search strategies until a result is found.

    Strategy 1 - strict field filters : track:<clean_name> artist:<artist>
    Strategy 2 - parsed dash split    : track:<title_part> artist:<artist_part>
    Strategy 3 - loose combined       : <artist> <clean_name>
    Strategy 4 - name only            : <clean_name>

    Returns the best matching track dict, or None if all strategies miss.
    """
    clean_name = _clean_title(name)
    parsed_artist, parsed_title = _parse_artist_and_title(name, artist)

    strategies = [
        ("strict",    f"track:{clean_name} artist:{artist}"),
        ("parsed",    f"track:{parsed_title} artist:{parsed_artist}"),
        ("loose",     f"{artist} {clean_name}"),
        ("name only", clean_name),
    ]

    for label, query in strategies:
        items = _raw_search(access_token, query)
        if items:
            best = _pick_best_track(items, artist or parsed_artist)
            if best:
                print(f"    [strategy: {label}] -> '{best['name']}' by {best['artists'][0]['name']}")
                return best

    return None


# ── SpotifyClient ──────────────────────────────────────────────────────────────

class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.__access_token: Optional[str] = None
        self.__set_new_access_token()
        self.__user_id: Optional[str] = self.get_user_id()

    def __set_new_access_token(self) -> None:
        sp_oauth = SpotifyOAuth(
            client_id=self.__client_id,
            client_secret=self.__client_secret,
            redirect_uri=self.redirect_uri,
            scope=" ".join([
                "playlist-read-private",
                "playlist-read-collaborative",
                "playlist-modify-private",
                "playlist-modify-public",
            ]),
            cache_path=".spotify_token_cache",
            open_browser=True,
        )
        token_info = sp_oauth.get_cached_token()
        if not token_info:
            auth_url = sp_oauth.get_authorize_url()
            print(f"\nOpen this URL to authorize Spotify:\n{auth_url}\n")
            response_url = input("Paste the redirect URL here: ").strip()
            code = sp_oauth.parse_response_code(response_url)
            token_info = sp_oauth.get_access_token(code)

        self.__access_token = token_info["access_token"]

    def get_user_id(self) -> Optional[str]:
        response = get_user_id_api(access_token=self.__access_token)
        if response is None:
            return None
        return response.json().get("id")

    def get_user_playlists(self) -> Optional[List[BasePlaylist]]:
        """Fetches ALL playlists, paging through results automatically."""
        all_playlists: List[BasePlaylist] = []
        offset = 0
        limit = 50

        while True:
            response = get_user_playlists_api(
                access_token=self.__access_token, offset=offset, limit=limit
            )
            if response is None:
                return None

            data = response.json()
            items = data.get("items", [])
            for item in items:
                all_playlists.append(
                    BasePlaylist(
                        id=item["id"],
                        name=item["name"],
                        uri=item["uri"],
                    )
                )

            if len(items) < limit:
                break
            offset += limit

        return all_playlists

    def get_playlist_tracks(self, playlist: BasePlaylist) -> List[BaseSong]:
        """Fetch ALL tracks from a Spotify playlist, paging automatically."""
        tracks: List[BaseSong] = []
        offset = 0

        while True:
            response = get_playlist_tracks_api(
                access_token=self.__access_token,
                playlist_id=playlist.id,
                offset=offset,
            )
            if response is None:
                break

            data = response.json()
            items = data.get("items", [])

            for item in items:
                track = item.get("track")
                # track can be None if it was removed from Spotify
                if not track:
                    continue
                artists = ", ".join(a["name"] for a in track.get("artists", []))
                tracks.append(BaseSong(
                    id=track["id"],
                    name=track["name"],
                    uri=track["uri"],
                ))
                # Store artist on the song so YouTube search can use it
                tracks[-1].artist = artists

            if len(items) < 100:
                break
            offset += 100

        return tracks

    def search_track(self, name: str, artist: str) -> Optional[BaseSong]:
        best = search_track_api(
            access_token=self.__access_token, name=name, artist=artist
        )
        if best is None:
            print(f"  [MISS] No Spotify match for '{name}' by '{artist}'.")
            return None

        return BaseSong(
            id=best["id"],
            name=best["name"],
            uri=best["uri"],
        )

    def create_playlist(
        self, name: Optional[str] = None, description: Optional[str] = None
    ) -> Optional[BasePlaylist]:
        response = create_playlist_api(
            access_token=self.__access_token,
            name=name if name else create_default_playlist_name(),
            description=description if description else create_default_playlist_desc(),
        )
        if response is None:
            return None

        data = response.json()
        return BasePlaylist(id=data["id"], name=data["name"], uri=data["uri"])

    def add_songs(self, playlist: BasePlaylist, songs: List[BaseSong]) -> bool:
        """Add songs in batches of 100 (Spotify API limit)."""
        remaining = list(songs)
        while remaining:
            batch = remaining[:100]
            is_success = add_songs_to_playlist_api(
                access_token=self.__access_token,
                playlist_id=playlist.id,
                song_uris=[song.uri for song in batch],
            )
            if not is_success:
                print(f"  ERROR: Failed to insert a batch of {len(batch)} songs.")
                return False
            remaining = remaining[100:]
        return True
import datetime


def print_spotify_api_error(status_code):
    print(f"Spotify API failed with the status code {status_code}")

## TODO: [SP-49] update default playlist name and desc
def create_default_playlist_name() -> str:
    now = datetime.datetime.now()
    return f"Playlist {now.year}.{now.month}.{now.day} {now.hour}:{now.minute}" 

## TODO: [SP-49] update default playlist name and desc
def create_default_playlist_desc() -> str:
    return "This playlist is created by a bot! How cool is that?!?\nCheck here for more info: https://github.com/kevinthai21/YT-Spotify"

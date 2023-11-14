
class Song:
    def __init__(self, id, name, uri):
        self.id = id
        self.name = name
        self.uri = uri

class Playlist:
    def __init__(self, id, playlist_name, uri = ""):
        self.name = playlist_name # str
        self.id = id
        self.songs = [] # List[Song]
        self.uri = uri

    def size(self) -> int:
        return len(self.songs)
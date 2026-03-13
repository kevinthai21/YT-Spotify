YouTube-To-Spotify Playlist Transfer
=========

Information
-----
The program will take a YouTube playlist and save it into a new Spotify playlist!

How to Run:
- Set up pipenv: `pipenv install`.
- Run the main method: `pipenv run python3 main.py`.

Note
-----
- Keep in mind that the music playlist from YouTube needs to be public or unlisted.
- The program takes in songs (from YouTube) that are in two different formats: 
    * **Video Title: "Treasure", Channel: "Bruno Mars"** or 
    * **Video Title: "Treasure", Channel: "Bruno Mars - Topic"**
      * (It can take music videos or lyric videos but the program is less likely to find it on Spotify)

- This uses Spotify API and the Google OAuth Platform. Be sure to create an `.env` that
would store the expected information that the program requires. Here is an example of what the `.env` should look like:
```
SPOTIFY_CLIENT_ID="SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET="SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI="SPOTIFY_REDIRECT_URI"
CLIENT_SECRETS_FILE="CLIENT_SECRETS_FILE"
```

Inspiration
-----
When transferring playlists from one music platform to another platform, I found it difficult and extremely time-consuming to copy a playlist from one platform. Since it took a long time and it takes the same number of steps for each song, it was best to try to automate the process.
YouTube-To-Spotify Playlist Transfer
=========

Information
-----
The program takes a music playlist from YouTube and creates a new playlist on Spotify.

The program will ask the user for information on the playlist the user wants to copy from (name and link). Then, it will ask for the Spotify login information (Note: It will not save the login information.).

After the program saved the user information, the program will scrape the names of the songs and artists from the YouTube playlist. It will create a new playlist and will transfer all of the songs.
If there are some songs that are not listed, there is a log in the console of songs that are added and those that aren't.

I wrote this program in JavaScript. It uses `NodeJS`, `Puppeteer`, and `readline-sync`.
`Puppeteer` is a Node library that controls a headless Chrome or Chromium. `Readline-sync` is a library that takes input from the user and saves the information for the program to use.
To run the program, the user should install these extensions by typing `npm install puppeteer` and `npm install readline-sync`.
Then, the user should type `node node.js` to run the program.

Note
-----
- Keep in mind that the music playlist from YouTube needs to be public or unlisted.
- The program takes in songs (from YouTube) that are in two different formats: 
    * **Video Title: "Treasure", Channel: "Bruno Mars"** or 
    * **Video Title: "Treasure", Channel: "Bruno Mars - Topic"**
      * (It can take music videos or lyric videos but the program is less likely to find it on Spotify)
- The program will not save the Spotify login information.

Inspiration
-----
When transferring playlists from one music platform to another platform, I found it difficult and extremely time-consuming to copy a playlist from one platform. Since it took a long time and it takes the same number of steps for each song, it was best to try to automate the process.

I initially wanted to create a Google Chrome extension to perform these actions; however, Google Chrome extensions were not the best choice to transfer playlists. 

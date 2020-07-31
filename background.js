// Created by Kevin Thai

// The file will take the link from popup and take each video from the playlist and put
// it into a new Spotify playlist.

var test = document.getElementById("transferButton"); // checks the button press
var input = document.getElementById("yt-link"); // gets the input values
var link;

// if the button is not Null, then checks if the button has been pressed.
if(test) {
    test.onclick = function() { definePlaylist(input.value)};
}

/* definePlaylist() gets the link and saves the link */
function definePlaylist(ytLink) {
    link = ytLink;
    alert(link);
}
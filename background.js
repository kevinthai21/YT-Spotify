// Created by Kevin Thai

// The file will take the link from popup and take each video from the playlist and put
// it into a new Spotify playlist.

var test = document.getElementById("transferButton"); // checks the button press
var input = document.getElementById("yt-link"); // gets the input values
var link;

var mvName=[];
var channelName=[];

// if the button is not Null, then checks if the button has been pressed.
if(test) {
    test.onclick = function() { definePlaylist(input.value)};
}

/* definePlaylist() gets the link and saves the link */
function definePlaylist(ytLink) {
    // const init = "https://";
    // link = "";
    // // if the link provided doesn't have the "https", add it.
    // if (!link.includes(init)) {
    //     link = link.concat(init,ytLink);
    // }
    // else {
    //     link = ytLink;
    //     console.log(link);
    // }


    link = ytLink

    // start the transfer process.
    transferPlaylist();
    alert(link);
}

function transferPlaylist() {
    chrome.tabs.create({ url : link});
    // var win = window.open(link, "_blank");
    // win.focus();

    getMusic();
}

function getMusic() {
    mvName.push("SOLO");
    channelName.push("JENNIE - Topic");
    alert(mvName);
    alert(channelName);
    chrome.tabs.create({ url : "https://www.google.com"});
}

function done() {
    alert("Done transferring playlist!");
}
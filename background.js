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
    // alert(link);
}

function transferPlaylist() {
    chrome.tabs.create({ url : link, active: false});
    // var win = window.open(link, "_blank");
    // win.focus();

    getMusic();
}

function getMusic() {
    // var found = $x("");
    // alert(found);
    // alert(getElementByXpath("/html/body/ytd-app/div/ytd-page-manager/ytd-browse[3]/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[1]/div[2]/a/div/h3/span"));
    // alert(mvName);
    // alert(channelName);
    window.location = link;
    //var req = Spry.Utils.loadURL("GET", link, true);
    var req = loadURL("http://www.youtube.com");
    alert(req);
    // const content = element.innerHTML;
    // element.innerHTML = link;
    var name = document.getElementById("yt-link").value;
    //var name = getElementByXpath("/html/body/ytd-app/div/ytd-page-manager/ytd-browse[3]/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[1]/div[2]/a/div/h3/span");
    alert(name);
}

function done() {
    alert("Done transferring playlist!");
}

function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue;
}
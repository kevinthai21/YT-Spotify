// Created by Kevin Thai

// The file will take in a URL of a YouTube playlist and it will save it into
// a Spotify playlist for you. It requires a YouTube playlist (public/unlisted)
// and login information for Spotify (note: that information won't be saved).

// This will take in videos that are in a format that is mostly used for
// YouTube Music. The videos would be from the artist themselves with the
// name of the song as the title of the video.
// Ex.  Title: "Treasure", Channel: "Bruno Mars" or
//      Title: "Treasure", Channel: "Bruno Mars - Topic"
const puppeteer = require('puppeteer');
var listSong = [];
var listChannel = [];
let spotifyEmail;
let spotifyPass;
let totalNum;
let playlistName;

/*
This function takes in a URL of a YouTube playlist and will save each individual 
song and its artist into an array.
*/
async function scrapePlaylist(url) {
    console.log("Starting transfer...\n");
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url);
    await page.setViewport({
        width: 1200,
        height: 800
    });
    

    console.log("Scrolling...\n");
    await page.evaluate( ()=> {
        window.scrollBy(0,10000);
    });
    await page.waitFor(6000);
    await page.screenshot({path:'1000.png'});

    console.log("Time to get info!\n");

    // saves the number of videos/songs in the playlist
    const[el] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-playlist-sidebar-renderer/div/ytd-playlist-sidebar-primary-info-renderer/div[1]/yt-formatted-string[1]');
    const txtNumber= await el.getProperty('text');
    let nameNumber = await txtNumber.jsonValue();
    nameNumber = JSON.stringify(nameNumber);
    nameNumber = nameNumber.replace('{"runs":[{"text":"','');
    nameNumber = nameNumber.replace(' videos"}]}', '');
    totalNum = parseInt(nameNumber);
    console.log(totalNum);

    // the for-loop saves the title and channel from each song in the playlist
    var index;
    for (index =1; index < totalNum + 1; index++) {
        console.log(index);
        
        // saves the name of the song
        const[el2] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[' + index + ']/div[2]/a/div/h3/span');
        const txtSong = await el2.getProperty('textContent');
        let nameSong = await txtSong.jsonValue();
        nameSong = JSON.stringify(nameSong);
        nameSong = nameSong.replace(/\\n/g,'');
        nameSong = nameSong.replace(/  +/g, '').replace(/"+/g,'');
        nameSong = nameSong.replace('Music Video', 'MV').replace('MV', '');

        // if a video is deleted, do not save it.
        if(nameSong == "[Deleted video]") {
            continue;
        }

        // saves the name of the channel that posted the song (relates to the artist).
        const[el3] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[' + index + ']/div[2]/a/div/ytd-video-meta-block/div[1]/div[1]/ytd-channel-name/div/div/yt-formatted-string/a');
        const txtChannel = await el3.getProperty('text');
        let nameChannel = await txtChannel.jsonValue();
        nameChannel = JSON.stringify(nameChannel);
        nameChannel = nameChannel.replace(/"+/g,'').replace(' - Topic', '').replace('OFFICIAL', '').replace('Official','');
        nameChannel = nameChannel.replace("YouTube Channel", '');
        nameChannel = nameChannel.replace("BANGTANTV", "BTS"); // This is a special case for BTS.
        console.log(nameSong, nameChannel);
        listSong.push(nameSong);
        listChannel.push(nameChannel);
    }
    console.log(listSong);
    console.log(listChannel);
    await browser.close();
    await makeSpotifyPlaylist();
}

/*
This function will login with Spotify details and create a new playlist.
After a new playlist is created, it will save the songs from the YouTube
playlist into this new playlist on Spotify.

For debugging purposes, there will be screenshots saved to see if the
program is working correctly.
*/
async function makeSpotifyPlaylist() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({
        width: 1200,
        height: 800
    });
    await page.goto('https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F');
    await page.screenshot({path:'spotify.png'});
    
    // It will input the login details. The program won't save the login details.
    const inputUser = await page.$x('/html/body/div[1]/div[2]/div/form/div[1]/div/input');
    // await inputUser[0].type('');
    await page.screenshot({path:'spotify.png'});
    const inputPass = await page.$x('/html/body/div[1]/div[2]/div/form/div[2]/div/input');
    // await inputPass[0].type('');
    await page.screenshot({path:'spotify.png'});

    const buttonLogin = await page.$x('/html/body/div[1]/div[2]/div/form/div[3]/div[2]/button');
    await buttonLogin[0].click();
    await page.waitFor(5000);

    // This will create a new, empty playlist.
    await page.screenshot({path:'spotify.png'});
    await page.click('button.fcdf941c8ffa7d0878af0a4f04aa05bb-scss');

    const inputPlaylistName = await page.$x('/html/body/div[4]/div/div[3]/div/div[1]/div/div/input');
    await inputPlaylistName[0].type('Test playlist_1');
    await page.screenshot({path:'screenshots/spotify_1_test.png'});

    const buttonCreate = await page.$x('/html/body/div[4]/div/div[3]/div/div[2]/div[2]/button');
    await buttonCreate[0].click();
    await page.screenshot({path:'screenshots/spotify_2_created.png'});

    const buttonSearch = await page.$x('/html/body/div[4]/div/div[2]/div[2]/nav/ul/li[2]/a');
    await buttonSearch[0].click();
    await page.screenshot({path:'screenshots/spotify_3_search.png'});

    // This for-loop will search the song in Spotify. Then, it will add it to the playlist.
    let index;
    for (index = 0; index < totalNum; index++) {
        const inputSong = await page.$x('/html/body/div[4]/div/div[2]/div[1]/header/div[3]/div/div/input');

        await page.goto('https://open.spotify.com/search/'+ listSong[index]+ '%20' + listChannel[index]);
        await page.waitFor(3000);
        await page.screenshot({path:'screenshots/spotify_4_searchResults.png'});

        try {
            const foundSong = await page.$x('/html/body/div[4]/div/div[2]/div[4]/div[1]/div/div[2]/div/div/div[2]/div/div/div/section[2]/div/div[2]/div[1]/div/div/div[3]');
            await foundSong[0].click({button:'right'});
            await page.waitFor(3000);
            await page.screenshot({path:'screenshots/spotify_5_options.png'});


            const buttonAdd = await page.$x('/html/body/div[4]/div/nav[1]/div[4]');
            await buttonAdd[0].click();
            await page.waitFor(3000);
            await page.screenshot({path:'screenshots/spotify_6_setOfPlaylists.png'});

            const buttonPlaylist = await page.$x('/html/body/div[4]/div/div[3]/div/div[4]/div/div/div[2]/div[1]/div/div/div/div');
            await buttonPlaylist[0].click();
            await page.waitFor(3000);
            await page.screenshot({path:'screenshots/spotify_7_done.png'});
            console.log("Successfully added " + listSong[index] + ' - ' + listChannel[index]);
        }
        catch(err) {
            console.log("Song not found: " + listSong[index] + ' - ' + listChannel[index]);
            continue;
        }
    }
    await browser.close();
}

scrapePlaylist('https://www.youtube.com/playlist?list=PL1_xnl_NJ7lCbr3JBcBlRuMm2rlPdw1lw');

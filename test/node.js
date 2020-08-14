// Created by Kevin Thai

// The file will take in a URL of a YouTube playlist and it will save it into
// a Spotify playlist for you. It requires a YouTube playlist (public/unlisted)
// and login information for Spotify (note: that information won't be saved).

// This will take in videos that are in a format that is mostly used for
// YouTube Music. The videos would be from the artist themselves with the
// name of the song as the title of the video.
// Ex.  Title: "Treasure", Channel: "Bruno Mars" or
//      Title: "Treasure", Channel: "Bruno Mars - Topic"

let playlistName;
let link;
let spotifyEmail;
let spotifyPass;
let ready = false;
let failedTransfers = [];


const reader = require('readline-sync');

// takes information from the user.
while (ready == false) {
    playlistName = reader.question("Enter a name for the playlist: ");
    link = reader.question('Enter your YouTube playlist link: ');
    console.log("Please enter your Spotify login. Don't worry, it won't be saved elsewhere.");
    spotifyEmail = reader.question('Enter your Spotify email/username: ');
    spotifyPass = reader.question('Enter your Spotify password: ', { hideEchoBack: true});
    let spotifyPassTest;
    spotifyPassTest = reader.question('Re-enter your Spotify password: ', { hideEchoBack: true});
    while(spotifyPass != spotifyPassTest)
    {
        console.log("The passwords are different! Try re-entering again...");
        spotifyPass = reader.question('Enter your Spotify password: ', { hideEchoBack: true});
        spotifyPassTest = reader.question('Re-enter your Spotify password: ', { hideEchoBack: true});
    }
    let spotifyPassEncrypt = "";
    for(index=0; index<spotifyPass.length; index++) {
        spotifyPassEncrypt = spotifyPassEncrypt + "*";
    }

    console.log("Your information: ");
    console.log("<Playlist name>: " + playlistName);
    console.log("<Playlist link>: " + link);
    console.log("<Spotify username/email>: " + spotifyEmail);
    console.log("<Spotify password>: " + spotifyPassEncrypt);

    if(reader.keyInYN("Is the information correct?")) { 
        ready = true;
    }
}

const puppeteer = require('puppeteer');
var listSong = [];
var listChannel = [];
let totalNum;

/*
This function takes in a URL of a YouTube playlist and will save each individual 
song and its artist into an array.
*/
async function scrapePlaylist(url) {
    ready = false;
    console.log("\n");
    console.log("Opening browser...\n");
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Configure the navigation timeout
    await page.setDefaultNavigationTimeout(0);

    // checks the link that user provided
    try {
        if(url.includes("https://www.youtube.com") == false) {
            throw new Error("Not valid link.");
        }
        await page.goto(url);
    }
    catch (err) {
        console.log("Invalid link. Either have the playlist be public/unlisted");
        console.log("Remember to have the link be like this 'https://www.youtube.com...'");
        return process.exit(1);
    }
        await page.setViewport({
            width: 1200,
            height: 800
        });
        
        await page.evaluate( ()=> {
            window.scrollBy(0,10000);
        });
        await page.waitFor(6000);
        // await page.screenshot({path:'1000.png'});

        console.log("Time to copy info!\n");

    
        // saves the number of videos/songs in the playlist
        const[el] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-playlist-sidebar-renderer/div/ytd-playlist-sidebar-primary-info-renderer/div[1]/yt-formatted-string[1]');
        const txtNumber= await el.getProperty('text');
        let nameNumber = await txtNumber.jsonValue();
        nameNumber = JSON.stringify(nameNumber);
        nameNumber = nameNumber.replace('{"runs":[{"text":"','');
        nameNumber = nameNumber.replace(' videos"}]}', '');
        totalNum = parseInt(nameNumber);

        let indexTotalNum = totalNum;

        // the for-loop saves the title and channel from each song in the playlist
        var index;
        for (index =1; index < indexTotalNum + 1; index++) {            
            // saves the name of the song
            try {
                const[el2] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[' + index + ']/div[2]/a/div/h3/span');
                const txtSong = await el2.getProperty('textContent');
                nameSong = await txtSong.jsonValue();
                nameSong = JSON.stringify(nameSong);

                nameSong = nameSong.replace(/\\n/g,'');
                nameSong = nameSong.replace(/  +/g, '').replace(/"+/g,'');
                nameSong = nameSong.replace('Music Video', 'MV').replace('MV', '');
                nameSong = nameSong.replace(/[^ a-zA-Z0-9()]+/g, "").replace(/  +/g, '');
            

                // saves the name of the channel that posted the song (relates to the artist).
                const[el3] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[' + index + ']/div[2]/a/div/ytd-video-meta-block/div[1]/div[1]/ytd-channel-name/div/div/yt-formatted-string/a');
                const txtChannel = await el3.getProperty('text');
                let nameChannel = await txtChannel.jsonValue();
                nameChannel = JSON.stringify(nameChannel);
                nameChannel = nameChannel.replace(/"+/g,'').replace(' - Topic', '').replace('OFFICIAL', '').replace('Official','');
                nameChannel = nameChannel.replace("YouTube Channel", '');
                nameChannel = nameChannel.replace("BANGTANTV", "BTS"); // This is a special case for BTS.
                nameChannel = nameChannel.replace(/[^ a-zA-Z0-9()]+/g, "").replace(/  +/g, '');
                console.log(nameSong, nameChannel);
                listSong.push(nameSong);
                listChannel.push(nameChannel);
            }

            // A deleted video has been found.
            catch (err)
            {
                console.log("<Found deleted video..>");
                continue;
            }
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
    let numSuccess=0;
    console.log("Now transferring...");
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({
        width: 1200,
        height: 800
    });
    // Configure the navigation timeout
    await page.setDefaultNavigationTimeout(0);

    await page.goto('https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F');
    // await page.screenshot({path:'spotify.png'});
    
    // It will input the login details. The program won't save the login details.
    
    const inputUser = await page.$x('/html/body/div[1]/div[2]/div/form/div[1]/div/input');
    await inputUser[0].type(spotifyEmail);
    // await page.screenshot({path:'spotify.png'});
    const inputPass = await page.$x('/html/body/div[1]/div[2]/div/form/div[2]/div/input');
    await inputPass[0].type(spotifyPass);
    // await page.screenshot({path:'spotify.png'});

    const buttonLogin = await page.$x('/html/body/div[1]/div[2]/div/form/div[3]/div[2]/button');
    await buttonLogin[0].click();
    await page.waitFor(7000);

    // if can click on this successfully, it has logged in.
    try {
        // This will create a new, empty playlist.
        // await page.screenshot({path:'spotify.png'});
        await page.click('button.fcdf941c8ffa7d0878af0a4f04aa05bb-scss');

    }
    catch(err) {
        browser.close
        console.log("Failed to login Spotify. Invalid username or password.");
        return process.exit(1);
    }

    const inputPlaylistName = await page.$x('/html/body/div[4]/div/div[3]/div/div[1]/div/div/input');
    await inputPlaylistName[0].type(playlistName);
    // await page.screenshot({path:'screenshots/spotify_1_test.png'});

    const buttonCreate = await page.$x('/html/body/div[4]/div/div[3]/div/div[2]/div[2]/button');
    await buttonCreate[0].click();
    // await page.screenshot({path:'screenshots/spotify_2_created.png'});

    const buttonSearch = await page.$x('/html/body/div[4]/div/div[2]/div[2]/nav/ul/li[2]/a');
    await buttonSearch[0].click();
    // await page.screenshot({path:'screenshots/spotify_3_search.png'});

    // This for-loop will search the song in Spotify. Then, it will add it to the playlist.
    let index;
    for (index = 0; index < totalNum; index++) {
        const inputSong = await page.$x('/html/body/div[4]/div/div[2]/div[1]/header/div[3]/div/div/input');

        await page.goto('https://open.spotify.com/search/'+ listSong[index]+ '%20' + listChannel[index]);
        await page.waitFor(3000);
        // await page.screenshot({path:'screenshots/spotify_4_searchResults.png'});

        try {
            const foundSong = await page.$x('/html/body/div[4]/div/div[2]/div[4]/div[1]/div/div[2]/div/div/div[2]/div/div/div/section[2]/div/div[2]/div[1]/div/div/div[3]');
            await foundSong[0].click({button:'right'});
            await page.waitFor(3000);
            // await page.screenshot({path:'screenshots/spotify_5_options.png'});


            const buttonAdd = await page.$x('/html/body/div[4]/div/nav[1]/div[4]');
            await buttonAdd[0].click();
            await page.waitFor(3000);
            // await page.screenshot({path:'screenshots/spotify_6_setOfPlaylists.png'});

            const buttonPlaylist = await page.$x('/html/body/div[4]/div/div[3]/div/div[4]/div/div/div[2]/div[1]/div/div/div/div');
            await buttonPlaylist[0].click();
            await page.waitFor(3000);
            // await page.screenshot({path:'screenshots/spotify_7_done.png'});
            console.log("Added " + listSong[index] + ' - ' + listChannel[index]);
            numSuccess += 1;
        }
        catch(err) {
            console.log("Failed to transfer " + listSong[index] + " - " + listChannel[index]);
            failedTransfers.push(listSong[index] + " - " + listChannel[index]);
            continue;            
        }
    }
    await browser.close();
    console.log("Sucessfully added " + numSuccess + "/" + totalNum + " songs!");
    console.log("Failed transfers: ");
    for(index=0; index<failedTransfers.length; index++){
        console.log(failedTransfers[index]);
    }
    return process.exit(0);
}

if (ready)  {
    scrapePlaylist(link);
}
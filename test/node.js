const puppeteer = require('puppeteer');
var listSong = [];
var listChannel = [];
let spotifyEmail;
let spotifyPass;


async function scrapePlaylist(url) {
    console.log("Starting transfer...");
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url);
    await page.setViewport({
        width: 1200,
        height: 800
    });

    console.log("<Scrolling...>");
    await page.evaluate( ()=> {
        window.scrollBy(0,10000);
    });
    await page.waitFor(6000);
    // await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
    // window.scrollBy(0, 300);
    await page.screenshot({path:'1000.png'});

    console.log("<Time to get info!>");

    const[el] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-playlist-sidebar-renderer/div/ytd-playlist-sidebar-primary-info-renderer/div[1]/yt-formatted-string[1]');
    const txtNumber= await el.getProperty('text');
    let nameNumber = await txtNumber.jsonValue();
    nameNumber = JSON.stringify(nameNumber);
    nameNumber = nameNumber.replace('{"runs":[{"text":"','');
    nameNumber = nameNumber.replace(' videos"}]}', '');
    let totalNum = parseInt(nameNumber);

    var index;
    for (index =1; index < totalNum + 1; index++) {
        console.log(index);
        const[el2] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[' + index + ']/div[2]/a/div/h3/span');
        const txtSong = await el2.getProperty('textContent');
        let nameSong = await txtSong.jsonValue();
        nameSong = JSON.stringify(nameSong);
        nameSong = nameSong.replace(/\\n/g,'');
        nameSong = nameSong.replace(/  +/g, '').replace(/"+/g,'');
        nameSong = nameSong.replace('Music Video', 'MV').replace('MV', '');
        if(nameSong == "[Deleted video]") {
            continue;
        }

        const[el3] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[' + index + ']/div[2]/a/div/ytd-video-meta-block/div[1]/div[1]/ytd-channel-name/div/div/yt-formatted-string/a');
        const txtChannel = await el3.getProperty('text');
        let nameChannel = await txtChannel.jsonValue();
        nameChannel = JSON.stringify(nameChannel);
        nameChannel = nameChannel.replace(/"+/g,'').replace(' - Topic', '').replace('OFFICIAL', '').replace('Official','');
        nameChannel = nameChannel.replace("YouTube Channel", '');
        console.log(nameSong, nameChannel);
        listSong.push(nameSong);
        listChannel.push(nameChannel);
    }
    console.log(listSong);
    console.log(listChannel);
    await browser.close();
    await makeNewPlaylist();
}

async function makeNewPlaylist() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setViewport({
        width: 1200,
        height: 800
    });
    await page.goto('https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2F');
    await page.screenshot({path:'spotify.png'});
    
    const inputUser = await page.$x('/html/body/div[1]/div[2]/div/form/div[1]/div/input');
    await page.screenshot({path:'spotify.png'});
    const inputPass = await page.$x('/html/body/div[1]/div[2]/div/form/div[2]/div/input');
    await page.screenshot({path:'spotify.png'});

    const buttonLogin = await page.$x('/html/body/div[1]/div[2]/div/form/div[3]/div[2]/button');
    await buttonLogin[0].click();
    await page.waitFor(8000);

    await page.screenshot({path:'spotify.png'});
    await page.click('button.fcdf941c8ffa7d0878af0a4f04aa05bb-scss');

    await browser.close();
}

scrapePlaylist('https://www.youtube.com/playlist?list=PLIdyziN9sUYuVDKKzkmJ-Epfx9DnJwb-G');


makeNewPlaylist();

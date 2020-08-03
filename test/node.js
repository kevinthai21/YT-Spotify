const puppeteer = require('puppeteer');

async function scrapePlaylist(url) {
    console.log("Hello \n my sweet prince");
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url);
    const[el] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[5]/div[2]/a/div/h3/span');
    const txtSong = await el.getProperty('textContent');
    let nameSong = await txtSong.jsonValue();
    nameSong = JSON.stringify(nameSong);
    nameSong = nameSong.replace(/\\n/g,'');
    nameSong = nameSong.replace(/  +/g, '').replace(/"+/g,'');

    const[el2] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]/ytd-playlist-video-renderer[5]/div[2]/a/div/ytd-video-meta-block/div[1]/div[1]/ytd-channel-name/div/div/yt-formatted-string/a');
    const txtChannel = await el2.getProperty('text');
    let nameChannel = await txtChannel.jsonValue();
    nameChannel = JSON.stringify(nameChannel);
    nameChannel = nameChannel.replace(/"+/g,'');

    const[el3] = await page.$x('/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-playlist-sidebar-renderer/div/ytd-playlist-sidebar-primary-info-renderer/div[1]/yt-formatted-string[1]');
    const txtNumber= await el3.getProperty('text');
    let nameNumber = await txtNumber.jsonValue();
    nameNumber = JSON.stringify(nameNumber);
    nameNumber = nameNumber.replace('{"runs":[{"text":"','');
    nameNumber = nameNumber.replace(' videos"}]}', '');
    console.log("Start here:");
    console.log(nameSong);
    console.log(nameChannel);
    console.log(nameNumber);


    browser.close();
}


scrapePlaylist('https://www.youtube.com/playlist?list=PLIdyziN9sUYuVDKKzkmJ-Epfx9DnJwb-G');
// -*- mode: js; coding: utf-8; fill-column: 80; -*-
//
// fetcher_looping.js
//

const fs                  = require('fs');
const { harFromMessages } = require('chrome-har');
const os                  = require('os');
const path                = require('path');
const { promisify }       = require('util');
const puppeteer           = require('puppeteer');
const { createGzip } = require('zlib');
const { pipeline } = require('stream');
const {
  createReadStream,
  createWriteStream
} = require('fs');
var sleep = require('sleep');

const height = 1280;
const width = 720;


// Experiment options.
const opts = {
    browser: {
        // Whether to run browser in `headless` mode.
        executablePath: '/usr/bin/chromium-browser',
        headless: true,
        // Time (in ms) to wait for browser launch to complete.
        timeout: 15000,
        // Whether to ignore HTTPS errors during navigation.
        ignoreHTTPSErrors: true,
        args: [ '--enable-features=NetworkService',
            '--ignore-certificate-errors',
            ],
    },

    nav: {
        // Maximum time to complete page navigation.
        timeout: 50000,
    },

    // Event types to observe.
    eventsToObserve: [
        'Page.loadEventFired',
        'Page.domContentEventFired',
        'Page.frameStartedLoading',
        'Page.frameAttached',
        'Network.requestWillBeSent',
        'Network.requestServedFromCache',
        'Network.dataReceived',
        'Network.responseReceived',
        'Network.resourceChangedPriority',
        'Network.loadingFinished',
        'Network.loadingFailed',
    ],

    // Temporary `User Data` directory.
    tmpUsrDataDir: path.join(os.tmpdir(), 'dejavu'),
};


async function load_page(site_url, out_fpath, trial, wait_mark) {
    
    for (i=0; i<trial; i++) {
        var har_file_name = out_fpath + "-" + i;
        // if (fs.existsSync(har_file_name)) {
        //     console.log(har_file_name + " exist.")
        // } else {
            const browser = await puppeteer.launch(opts.browser);
            const page    = await browser.newPage();

            await page.setCacheEnabled(false);

            // Register events listeners.
            const client = await page.target().createCDPSession();
            await client.send('Page.enable');
            await client.send('Network.enable');
            await page.setUserAgent('Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36');
            await page.setViewport({ width: width, height: height });

            // List of events for converting to HAR.
            const events = [];

            opts.eventsToObserve.forEach(method => {
                client.on(method, params => {
                    events.push({ method, params });
                });
            });

            
            var start = Date.now();
            await page.goto(site_url, {timeout: opts.nav.timeout,
                                   waitUntil: wait_mark});
            var elapsed_time = Date.now() - start;
            console.log("Load time %d = %f ms", i, elapsed_time);
            await page.close()

            const har = harFromMessages(events);
            await promisify(fs.writeFile)(har_file_name, JSON.stringify(har, null, 2));
            await browser.close(); 
        // }
        
    }

    // Generate the HAR file.
    // const har = harFromMessages(events);
    // har_file_name = out_fpath;
    // await promisify(fs.writeFile)(har_file_name, JSON.stringify(har, null, 2));
    // await sleep.msleep(500);

    // const gzip = createGzip();
    // const source = createReadStream(har_file_name);
    // const destination = createWriteStream(har_file_name + '.har.gz');

    // pipeline(source, gzip, destination, (err) => {
    //   if (err) {
    //     console.error('An error occurred:', err);
    //     process.exitCode = 1;
    //   }
    // });

    // fs.unlinkSync(har_file_name);
}

(() => {
    // Sleep for 2 second before launching the browser so that mahi2 has finished setup properly.
    // sleep.sleep(5);
    sleep.sleep(3);
    const EXIT_FAIL = 1;

    function showUsage(err) {
        console.warn("Usage: %s <URL> <output-file-path> <num-trial> " +
                     "[<load|domcontentloaded|networkidle0|networkidle2>]",
                     process.argv[1]);
        process.exit(err);
    };

    const args = process.argv.slice(2);
    if (args.length < 3 || args.length > 4) {
        showUsage(EXIT_FAIL);
    }

    var wait_mark = undefined;
    if (args.length == 4) {
        wait_mark = args[3];
        if (wait_mark !== 'load'             &&
            wait_mark !== 'domcontentloaded' &&
            wait_mark !== 'networkidle0'     &&
            wait_mark !== 'networkidle2') {
            console.error("Unknown event `%s` for wait_mark!", wait_mark);
            showUsage(EXIT_FAIL);
        }
    }

    // Path to `User Data`.
    // NOTE: Just to be sure that each request is as _new_ as it can be.
    opts.browser['userDataDir'] = opts.tmpUsrDataDir;

    console.log("Start loading page..");

    (async (site_url, out_fpath, num_trial, wait_mark) => {
        // By default, wait until 'networkidle2'.
        var wait_mark = typeof wait_mark !== 'undefined' ?
                wait_mark: 'load';
        // for (i=0; i<num_trial; i++) {
        //     var har_file_name = out_fpath + "-" + i;
        //     await load_page(site_url, har_file_name, i, wait_mark);
        // }
        await load_page(site_url, out_fpath, num_trial, wait_mark);
        sleep.sleep(1);
    })(args[0], args[1], args[2], wait_mark).catch(err => {
        console.error(err);
        process.exit(EXIT_FAIL);
    });    

    
})();

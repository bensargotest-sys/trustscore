const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

(async () => {
  const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
  const options = {logLevel: 'info', output: 'json', onlyCategories: ['performance'], port: chrome.port};
  const runnerResult = await lighthouse('https://trustscore-website.vercel.app', options);

  console.log('Performance score:', runnerResult.lhr.categories.performance.score * 100);
  
  await chrome.kill();
})();

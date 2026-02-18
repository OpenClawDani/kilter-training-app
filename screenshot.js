const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 800 });
  await page.goto('http://localhost:3001', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: '/tmp/kilter-screenshot.png', fullPage: false });
  console.log('Screenshot saved!');
  await browser.close();
})();

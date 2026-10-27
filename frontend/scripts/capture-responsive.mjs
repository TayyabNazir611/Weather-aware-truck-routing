/* global document, innerWidth */import { chromium } from 'playwright'
const browser=await chromium.launch({channel:'chrome',headless:true})
for(const width of [320,375,414,768]){
 const page=await browser.newPage({viewport:{width,height:1000}})
 await page.goto('http://127.0.0.1:5173');await page.getByRole('button',{name:/Explore a recorded trip/}).click();await page.locator('[data-map-ready="true"]').waitFor({timeout:45000});await page.waitForTimeout(1200);await page.screenshot({path:`../docs/screenshots/live-map-${width}.png`,fullPage:true});console.log(width,'overflow',await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth));await page.close()
}
await browser.close()


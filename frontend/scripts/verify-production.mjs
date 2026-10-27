import { chromium } from 'playwright'
const browser = await chromium.launch({ channel: 'chrome', headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('http://127.0.0.1:4173')
  await page.getByRole('button', { name: /Explore a recorded trip/ }).click()
  await page.locator('[data-map-ready="true"]').waitFor({ timeout: 45000 })
  const canvas = await page.locator('.map canvas').boundingBox()
  const routeCount = await page.locator('.route-card').count()
  if (!canvas || canvas.height < 300 || routeCount !== 3 || errors.length) throw new Error(JSON.stringify({ canvas, routeCount, errors }))
  await page.getByRole('slider').fill('48')
  await page.screenshot({ path: '../docs/screenshots/production-build.png', fullPage: true })
  console.log(JSON.stringify({ productionBuild: 'PASS', mapCanvasHeight: canvas.height, routeCount, errors }))
} finally { await browser.close() }

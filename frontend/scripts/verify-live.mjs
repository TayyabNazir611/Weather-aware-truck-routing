// Opt-in live verification; consumes provider quota. Run with both local servers up.
import { chromium } from 'playwright'
import { mkdir, writeFile } from 'node:fs/promises'
const browser = await chromium.launch({ channel: 'chrome', headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
  page.setDefaultTimeout(45000)
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto('http://127.0.0.1:5173')
  await page.getByLabel('Origin', { exact: true }).fill('Chicago, Illinois')
  await page.locator('.search-results button').first().click()
  await page.getByLabel('Destination', { exact: true }).fill('Merrillville, Indiana')
  await page.locator('.search-results button').first().click()
  await page.getByRole('button', { name: '10 miles', exact: true }).click()
  const pending = page.waitForResponse(r => r.url().endsWith('/api/routes/analyze/'), { timeout: 150000 })
  await page.getByRole('button', { name: 'Compare truck routes' }).click()
  const response = await pending
  const data = await response.json()
  if (!response.ok()) throw new Error(JSON.stringify(data))
  await page.locator('.route-card').first().waitFor()
  await page.locator('[data-map-ready="true"]').waitFor()
  await page.getByRole('slider').fill('48')
  await page.locator('.route-detail summary').click()
  await page.locator('.table-link').nth(1).click()
  await mkdir('../docs/screenshots', { recursive: true })
  await page.screenshot({ path: '../docs/screenshots/live-desktop.png', fullPage: true })
  const report = { status: response.status(), routes: data.routes.length, checkpointCounts: data.routes.map(r => r.checkpoints.length), recommended: data.recommended_id, warnings: data.warnings, browserErrors: errors, forecastFrames: data.heatmap.times.length }
  await writeFile('../docs/live-verification.json', JSON.stringify(report, null, 2))
  console.log(JSON.stringify(report))
  if (errors.length) throw new Error('Browser errors occurred')
} finally { await browser.close() }

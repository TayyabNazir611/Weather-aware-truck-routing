import { test, expect } from '@playwright/test'
import fs from 'node:fs'
const demo = JSON.parse(fs.readFileSync('public/demo.json', 'utf8'))

test.beforeEach(async ({ page }) => {
  // Deterministic browser tests do not depend on third-party tile servers.
  await page.route('https://tiles.openfreemap.org/styles/*', route => route.fulfill({ json: {
    version: 8, sources: {}, layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#e9edf1' } }],
  } }))
})

test('recorded trip, route selection, checkpoints and forecast scrubbing', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', e => errors.push(e.message))
  await page.goto('/')
  await page.getByRole('button', { name: /Explore a recorded trip/ }).click()
  await expect(page.locator('.route-card')).toHaveCount(3)
  await expect(page.locator('.map')).toHaveAttribute('data-map-ready', 'true', { timeout: 45000 })
  await expect(page.locator('.map')).toBeVisible()
  expect((await page.locator('.map canvas').boundingBox())!.height).toBeGreaterThan(300)
  await expect(page.getByText(/Not a current travel assessment/)).toBeVisible()
  await page.locator('.route-card').nth(1).click()
  await expect(page.locator('.route-card').nth(1)).toHaveAttribute('aria-pressed', 'true')
  await page.locator('.route-detail summary').click()
  await expect(page.locator('tbody tr')).toHaveCount(demo.routes[1].checkpoints.length)
  await page.locator('.table-link').first().click()
  await expect(page.getByRole('region', { name: 'Checkpoint details' })).toBeVisible()
  await page.getByRole('button', { name: 'Close checkpoint' }).click()
  const recommendation = await page.locator('.recommendation').innerText()
  let weatherRequests = 0
  page.on('request', request => { if (request.url().includes('/api/')) weatherRequests++ })
  await page.getByRole('slider').fill('48')
  await expect(page.getByText('+48h', { exact: true })).toBeVisible()
  await page.getByLabel('Show overlay').uncheck()
  expect(await page.locator('.recommendation').innerText()).toBe(recommendation)
  expect(weatherRequests).toBe(0)
  expect(errors).toEqual([])
  await page.screenshot({ path: '../docs/screenshots/desktop.png', fullPage: true })
})

test('complete form through REST response, spacing and errors', async ({ page }) => {
  await page.route('**/api/locations/search/**', route => route.fulfill({ json: { results: [{ label: 'Chicago, Illinois', coordinates: [-87.63, 41.88] }, { label: 'Gary, Indiana', coordinates: [-87.33, 41.47] }] } }))
  let interval = 0
  await page.route('**/api/routes/analyze/', route => {
    interval = route.request().postDataJSON().interval_miles
    return route.fulfill({ json: { ...demo, mode: 'live' } })
  })
  await page.goto('/')
  await page.getByLabel('Origin', { exact: true }).fill('Chicago')
  await page.getByRole('button', { name: 'Chicago, Illinois' }).click()
  await page.getByLabel('Destination', { exact: true }).fill('Gary')
  await page.getByRole('button', { name: 'Gary, Indiana' }).click()
  await page.getByLabel('Cargo weight').fill('41000')
  await page.getByRole('button', { name: '10 miles', exact: true }).click()
  await page.getByRole('button', { name: 'Compare truck routes' }).click()
  await expect(page.locator('.route-card')).toHaveCount(3)
  expect(interval).toBe(10)
  await page.getByRole('button', { name: '50 miles', exact: true }).click()
  await page.getByRole('button', { name: 'Compare truck routes' }).click()
  await expect(page.locator('.route-card')).toHaveCount(3)
  expect(interval).toBe(50)
  await page.route('**/api/routes/analyze/', route => route.fulfill({ status: 503, json: { error: { message: 'Weather provider quota reached.' } } }))
  await page.getByRole('button', { name: 'Compare truck routes' }).click()
  await expect(page.getByRole('alert')).toHaveText('Weather provider quota reached.')
  await expect(page.locator('.route-card')).toHaveCount(0)
})

for (const width of [320, 375, 414, 768]) {
  test(`responsive layout at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/')
    await page.getByRole('button', { name: /Explore a recorded trip/ }).click()
    await expect(page.locator('.route-card')).toHaveCount(3)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    await page.screenshot({ path: `../docs/screenshots/mobile-${width}.png`, fullPage: true })
  })
}

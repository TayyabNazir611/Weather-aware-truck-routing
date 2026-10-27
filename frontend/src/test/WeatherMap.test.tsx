import { render, waitFor } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import type { Analysis } from '../types'
import fixture from '../../public/demo.json'
const mocks = vi.hoisted(() => ({ created: vi.fn(), removed: vi.fn(), sources: {} as Record<string, { setData: ReturnType<typeof vi.fn> }>, visibility: vi.fn() }))
vi.mock('maplibre-gl', () => ({
  setWorkerUrl: vi.fn(), NavigationControl: class {},
  LngLatBounds: class { extend() { return this } },
  Map: class {
    constructor() { mocks.created() }
    addControl() {}
    on(event: string, callback: unknown) { if (event === 'load') queueMicrotask(callback as () => void) }
    addSource(id: string) { mocks.sources[id] = { setData: vi.fn() } }
    addLayer() {}
    getSource(id: string) { return mocks.sources[id] }
    fitBounds() {}
    setLayoutProperty(...args: unknown[]) { mocks.visibility(...args) }
    resize() {}
    remove() { mocks.removed() }
  },
}))
vi.mock('maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url', () => ({ default: 'mock-worker' }))
import { WeatherMap } from '../components/WeatherMap'

beforeEach(() => {
  vi.clearAllMocks()
  vi.stubGlobal('ResizeObserver', class { observe() {} disconnect() {} })
})

it('updates sources for selection and forecast without recreating the map', async () => {
  const data = fixture as unknown as Analysis
  // Make frame changes visible even if this recorded trip has uniformly Low weather.
  const changed = { ...data, heatmap: { ...data.heatmap, points: [{ coordinates: [-87, 41] as [number, number], risk: Array.from({ length: 49 }, (_, i) => i === 48 ? 4 as const : 0 as const) }] } }
  const { rerender, unmount } = render(<WeatherMap data={changed} selectedId="r1" hour={0} overlay onCheckpoint={vi.fn()}/>)
  await waitFor(() => expect(mocks.sources.corridor.setData).toHaveBeenCalled())
  const first = mocks.sources.corridor.setData.mock.lastCall![0]
  expect(first.features[0].properties.risk).toBe(0)
  rerender(<WeatherMap data={changed} selectedId="r2" hour={48} overlay={false} onCheckpoint={vi.fn()}/>)
  await waitFor(() => expect(mocks.sources.corridor.setData.mock.lastCall![0].features[0].properties.risk).toBe(4))
  expect(mocks.sources.routes.setData.mock.lastCall![0].features.at(-1).properties.id).toBe('r2')
  expect(mocks.visibility).toHaveBeenLastCalledWith('corridor-field', 'visibility', 'none')
  expect(mocks.created).toHaveBeenCalledTimes(1)
  unmount()
  expect(mocks.removed).toHaveBeenCalledTimes(1)
})

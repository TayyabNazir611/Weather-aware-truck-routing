import { useEffect, useRef, useState } from 'react'
import * as maplibregl from 'maplibre-gl'
import type { GeoJSONSource } from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { Feature, FeatureCollection } from 'geojson'
import { colors, type Analysis, type Checkpoint } from '../types'

const collection = (features: Feature[]): FeatureCollection => ({ type: 'FeatureCollection', features })
maplibregl.setWorkerUrl(workerUrl)
const severityColor: maplibregl.ExpressionSpecification = ['match', ['get', 'risk'], 0, colors[0], 1, colors[1], 2, colors[2], 3, colors[3], 4, colors[4], colors[5]]

export function WeatherMap({ data, selectedId, hour, overlay, onCheckpoint }: { data: Analysis | null; selectedId: string | null; hour: number; overlay: boolean; onCheckpoint: (point: Checkpoint) => void }) {
  const container = useRef<HTMLDivElement>(null)
  const map = useRef<maplibregl.Map | null>(null)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState('')
  const latest = useRef({ data, onCheckpoint })
  useEffect(() => { latest.current = { data, onCheckpoint } }, [data, onCheckpoint])
  useEffect(() => {
    if (!container.current) return
    let instance: maplibregl.Map
    try {
      instance = new maplibregl.Map({ container: container.current, style: import.meta.env.VITE_MAP_STYLE_URL || 'https://tiles.openfreemap.org/styles/positron', center: [-87.60, 41.70], zoom: 8.2, attributionControl: { compact: true } })
    } catch { setError('WebGL is unavailable. Route summaries and checkpoint forecasts remain available below.'); return }
    map.current = instance
    instance.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
    instance.on('error', () => setError('Some map tiles could not load. Check your connection; route details remain available.'))
    instance.on('load', () => {
      setError('')
      for (const id of ['corridor', 'routes', 'risk-segments', 'checkpoints']) instance.addSource(id, { type: 'geojson', data: collection([]) })
      // Blurred, severity-colored forecast samples: color represents risk, not point density.
      instance.addLayer({ id: 'corridor-field', type: 'circle', source: 'corridor', paint: {
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 3, 10, 7, 38, 10, 110, 14, 220],
        'circle-color': severityColor, 'circle-opacity': .38, 'circle-blur': .85,
      } })
      instance.addLayer({ id: 'route-casing', type: 'line', source: 'routes', paint: { 'line-color': '#ffffff', 'line-width': ['case', ['get', 'selected'], 9, 6], 'line-opacity': .95 } })
      instance.addLayer({ id: 'route-lines', type: 'line', source: 'routes', paint: { 'line-color': ['case', ['get', 'selected'], '#234de4', '#7f8eaf'], 'line-width': ['case', ['get', 'selected'], 5, 3], 'line-opacity': ['case', ['get', 'selected'], 1, .7] }, layout: { 'line-join': 'round', 'line-cap': 'round' } })
      instance.addLayer({ id: 'risk-lines', type: 'line', source: 'risk-segments', paint: { 'line-color': severityColor, 'line-width': 3 }, layout: { 'line-cap': 'round' } })
      instance.addLayer({ id: 'checkpoint-dots', type: 'circle', source: 'checkpoints', paint: { 'circle-radius': 5.5, 'circle-color': severityColor, 'circle-stroke-width': 2.5, 'circle-stroke-color': '#ffffff' } })
      instance.on('click', 'checkpoint-dots', e => {
        const id = e.features?.[0]?.properties?.id
        const point = latest.current.data?.routes.flatMap(r => r.checkpoints).find(p => p.id === id)
        if (point) latest.current.onCheckpoint(point)
      })
      instance.on('mouseenter', 'checkpoint-dots', () => { instance.getCanvas().style.cursor = 'pointer' })
      instance.on('mouseleave', 'checkpoint-dots', () => { instance.getCanvas().style.cursor = '' })
      setReady(true)
    })
    const observer = new ResizeObserver(() => instance.resize())
    observer.observe(container.current)
    return () => { observer.disconnect(); instance.remove(); map.current = null }
  }, [])
  useEffect(() => {
    if (!ready || !map.current || !data) return
    const bounds = new maplibregl.LngLatBounds()
    data.routes.forEach(r => r.geometry.coordinates.forEach(p => bounds.extend(p as [number, number])))
    map.current.fitBounds(bounds, { padding: { top: 80, bottom: 150, left: 65, right: 65 }, maxZoom: 12, duration: 700 })
  }, [ready, data])
  useEffect(() => {
    if (!ready || !map.current) return
    const selected = data?.routes.find(r => r.id === selectedId)
    const routes = [...(data?.routes || [])].sort((a, b) => Number(a.id === selectedId) - Number(b.id === selectedId))
    ;(map.current.getSource('routes') as GeoJSONSource).setData(collection(routes.map(r => ({ type: 'Feature', geometry: r.geometry, properties: { id: r.id, selected: r.id === selectedId } }))))
    ;(map.current.getSource('checkpoints') as GeoJSONSource).setData(collection((selected?.checkpoints || []).map(p => ({ type: 'Feature', geometry: { type: 'Point', coordinates: p.coordinates }, properties: { id: p.id, risk: p.risk ?? -1 } }))))
    // The route is blue for legibility; risk markers encode arrival-time weather.
  }, [ready, data, selectedId])
  useEffect(() => {
    if (!ready || !map.current) return
    const features: Feature[] = (data?.heatmap.points || []).map(p => ({ type: 'Feature', geometry: { type: 'Point', coordinates: p.coordinates }, properties: { risk: p.risk[hour] ?? -1 } }))
    ;(map.current.getSource('corridor') as GeoJSONSource).setData(collection(features))
    map.current.setLayoutProperty('corridor-field', 'visibility', overlay ? 'visible' : 'none')
  }, [ready, data, hour, overlay])
  return <><div ref={container} className="map" data-map-ready={ready} aria-label="Interactive truck route and weather map"/>{error && <p className="map-error" role="status">{error}</p>}</>
}

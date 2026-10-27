import type { Analysis, Location, Trip } from './types'
const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${base}/api/${path}`, options)
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const error = data?.error
    throw new Error(error?.details ? `${error.message} ${JSON.stringify(error.details)}` : error?.message || `Request failed (${response.status}).`)
  }
  return data as T
}
export const searchLocations = (q: string, signal: AbortSignal) => request<{ results: Location[] }>(`locations/search/?q=${encodeURIComponent(q)}`, { signal })
export const analyzeTrip = (trip: Trip, signal: AbortSignal) => request<Analysis>('routes/analyze/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(trip), signal })
export const loadDemo = async (signal?: AbortSignal): Promise<Analysis> => {
  const result = await fetch('/demo.json', { signal })
  if (!result.ok) throw new Error('The recorded demonstration is unavailable.')
  return result.json()
}

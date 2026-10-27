import { useEffect, useId, useState } from 'react'
import { searchLocations } from '../api'
import type { Location } from '../types'

export function LocationSearch({ label, value, onChange }: { label: string; value: Location | null; onChange: (value: Location | null) => void }) {
  const id = useId()
  const [query, setQuery] = useState(value?.label || '')
  const [results, setResults] = useState<Location[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    if (value || query.length < 3) return
    const controller = new AbortController()
    const timer = setTimeout(() => {
      setBusy(true); setError('')
      searchLocations(query, controller.signal).then(({ results }) => setResults(results))
        .catch(e => { if (e.name !== 'AbortError') setError(e.message) })
        .finally(() => { if (!controller.signal.aborted) setBusy(false) })
    }, 350)
    return () => { clearTimeout(timer); controller.abort() }
  }, [query, value])
  return <div className="location-field">
    <label htmlFor={id}>{label}</label>
    <input id={id} value={value?.label ?? query} placeholder={label === 'Origin' ? 'City, address or ZIP' : 'Where are you headed?'} autoComplete="off" required
      aria-describedby={`${id}-status`} onChange={e => { setQuery(e.target.value); onChange(null); setResults([]); setBusy(false) }} />
    <span className="field-status" id={`${id}-status`} role="status">{busy ? 'Searching…' : error || (query.length >= 3 && !value && !results.length ? 'Select a matching location from the results.' : '')}</span>
    {!value && results.length > 0 && <ul className="search-results" aria-label={`${label} suggestions`}>{results.map(result => <li key={`${result.label}-${result.coordinates}`}><button type="button" onClick={() => { onChange(result); setQuery(result.label); setResults([]) }}>{result.label}</button></li>)}</ul>}
  </div>
}

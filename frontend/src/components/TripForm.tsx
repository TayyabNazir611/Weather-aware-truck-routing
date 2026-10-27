import { useState } from 'react'
import { LocationSearch } from './LocationSearch'
import type { Location, Trip } from '../types'

function initialDeparture() {
  const date = new Date(Date.now() + 3600000)
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}
export function TripForm({ busy, onSubmit, onDirty }: { busy: boolean; onSubmit: (trip: Trip) => void; onDirty: () => void }) {
  const [origin, setOrigin] = useState<Location | null>(null)
  const [destination, setDestination] = useState<Location | null>(null)
  const [departure, setDeparture] = useState(initialDeparture)
  const [weight, setWeight] = useState('35000')
  const [interval, setInterval] = useState(25)
  const [error, setError] = useState('')
  return <form id="trip-form" onChange={onDirty} onSubmit={e => {
    e.preventDefault(); setError('')
    if (!origin || !destination) return setError('Select an origin and destination from the search results.')
    const date = new Date(departure)
    if (!Number.isFinite(date.getTime()) || date.getTime() < Date.now() - 300000 || date.getTime() > Date.now() + 5 * 86400000) return setError('Choose a departure between now and five days ahead.')
    if (origin.coordinates.join() === destination.coordinates.join()) return setError('Choose different origin and destination locations.')
    onSubmit({ origin, destination, departure: date.toISOString(), load_lb: Number(weight), interval_miles: interval })
  }}>
    <fieldset disabled={busy}>
      <LocationSearch label="Origin" value={origin} onChange={value => { setOrigin(value); onDirty() }}/>
      <LocationSearch label="Destination" value={destination} onChange={value => { setDestination(value); onDirty() }}/>
      <label htmlFor="departure">Departure</label>
      <input id="departure" type="datetime-local" required value={departure} onChange={e => setDeparture(e.target.value)}/>
      <p className="field-hint">Local time · {Intl.DateTimeFormat().resolvedOptions().timeZone}</p>
      <label htmlFor="weight">Cargo weight <span>lb</span></label>
      <input id="weight" type="number" min="0" max="200000" step="1" required value={weight} onChange={e => setWeight(e.target.value)}/>
      <label htmlFor="interval">Weather checkpoint spacing</label>
      <div className="segmented" id="interval" role="group" aria-label="Weather checkpoint spacing">{[10, 25, 50].map(n => <button key={n} type="button" aria-pressed={interval === n} onClick={() => { setInterval(n); onDirty() }}>{n} miles</button>)}</div>
    </fieldset>
    {error && <p role="alert" className="error">{error}</p>}
  </form>
}
